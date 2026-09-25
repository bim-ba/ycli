import asyncio
import time

import httpx
import pytest
from fastmcp.exceptions import AuthorizationError
from fastmcp.server.auth import AccessToken
from pydantic import ValidationError

from ycli.settings import RequestAuthConfig
from ycli.yandex import mcp
from ycli.yandex.tracker.dependencies import tracker_client

_REAL_ASYNC_CLIENT = httpx.AsyncClient


def approved(token="request-token", subject="user-1"):
    return AccessToken(token=token, client_id="identity-hub", scopes=[], subject=subject)


def test_request_auth_config_rejects_blank_organization_id(monkeypatch):
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", " ")
    with pytest.raises(ValidationError, match="non-whitespace identifier"):
        RequestAuthConfig()  # ty: ignore[missing-argument]


def test_credentials_provider_uses_request_mode(monkeypatch):
    monkeypatch.setattr(mcp, "get_access_token", lambda: approved())
    mcp.set_request_auth(mcp.RequestAuth("cloud-org"))
    assert mcp.credentials().iam_token == "request-token"


def test_request_credentials_require_authenticated_context(monkeypatch):
    monkeypatch.setattr(mcp, "get_access_token", lambda: None)
    mcp.set_request_auth(mcp.RequestAuth("cloud-org"))
    with pytest.raises(AuthorizationError, match="authenticated access token"):
        mcp.request_credentials()


def test_request_credentials_require_active_mode():
    mcp.set_request_auth(None)
    with pytest.raises(AuthorizationError, match="request-auth mode is not active"):
        mcp.request_credentials()


def test_credentials_fail_closed_when_auth_installed_without_mode(monkeypatch):
    from ycli.mcp.server import mcp as root_mcp

    root_mcp.auth = mcp.YandexBearerVerifier()
    mcp.set_request_auth(None)
    built: list[object] = []
    monkeypatch.setattr(
        mcp,
        "Credentials",
        lambda *a, **k: built.append(object()),
    )
    with pytest.raises(AuthorizationError, match="request-auth mode is not active"):
        mcp.credentials()
    assert built == []


def test_credential_repr_hides_secret_fields(monkeypatch):
    monkeypatch.setattr(mcp, "get_access_token", lambda: approved(token="secret-sentinel"))
    mcp.set_request_auth(mcp.RequestAuth("cloud-org"))
    credentials = mcp.credentials()
    assert "secret-sentinel" not in repr(credentials)
    assert "secret-sentinel" not in str(credentials)
    assert credentials.iam_token == "secret-sentinel"


def test_model_construct_field_set_matches_model_fields(monkeypatch):
    from ycli.settings import Credentials

    monkeypatch.setattr(mcp, "get_access_token", lambda: approved())
    mcp.set_request_auth(mcp.RequestAuth("cloud-org"))
    credentials = mcp.credentials()
    assert set(credentials.__pydantic_fields_set__) == set(Credentials.model_fields)


def test_request_credentials_do_not_read_env_per_request(monkeypatch):
    monkeypatch.setattr(mcp, "get_access_token", lambda: approved())
    mcp.set_request_auth(mcp.RequestAuth("startup-org"))

    def forbidden(*args, **kwargs):
        raise AssertionError("per-request settings/disk read")

    monkeypatch.setattr("ycli.settings.RequestAuthConfig.__init__", forbidden)
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "mutated-org")
    assert mcp.credentials().cloud_organization_id == "startup-org"


def test_request_credentials_use_only_approved_token(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "process-token")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "process-org")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud-org")
    monkeypatch.setattr(mcp, "get_access_token", lambda: approved())
    mcp.set_request_auth(mcp.RequestAuth("cloud-org"))
    credentials = mcp.request_credentials()
    assert credentials.oauth_token is None
    assert credentials.iam_token == "request-token"
    assert credentials.cloud_organization_id == "cloud-org"


def test_request_client_uses_approved_bearer_and_cloud_org(monkeypatch):
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud-org")
    monkeypatch.setattr(mcp, "get_access_token", lambda: approved())
    mcp.set_request_auth(mcp.RequestAuth("cloud-org"))
    client = tracker_client()
    session = client.priorities._session
    assert session.headers["Authorization"] == "Bearer request-token"
    assert session.headers["X-Cloud-Org-Id"] == "cloud-org"
    assert "X-Org-Id" not in session.headers
    assert "request-token" not in repr(client)


def install_userinfo(monkeypatch, handler):
    """Point the shared module-scoped userinfo client at a mock transport."""
    client = _REAL_ASYNC_CLIENT(
        transport=httpx.MockTransport(handler),
        timeout=mcp._USERINFO_TIMEOUT,
        follow_redirects=False,
    )
    monkeypatch.setattr(mcp, "_userinfo_client", client)
    monkeypatch.setattr(mcp, "_validation_shutting_down", False)
    return client


async def test_userinfo_client_is_shared_and_does_not_follow_redirects():
    assert mcp._userinfo_client is None
    await mcp.start_userinfo_client()
    client = mcp._userinfo_client
    assert client is not None
    assert client.follow_redirects is False
    assert mcp._userinfo_client is client


@pytest.mark.parametrize("status", [401, 403, 500])
async def test_userinfo_non_success_fails_closed(monkeypatch, status, loguru_sink):
    token = "rejected-sentinel"

    async def handler(request):
        assert request.headers["Authorization"] == f"Bearer {token}"
        assert request.extensions["timeout"] == {
            "connect": 2.0,
            "read": 3.0,
            "write": 3.0,
            "pool": 2.0,
        }
        return httpx.Response(status, json={"error": "rejected"})

    install_userinfo(monkeypatch, handler)
    assert await mcp.validate_identity_hub_token(token) is None
    assert token not in loguru_sink.getvalue()


async def test_userinfo_does_not_follow_redirect_to_attacker(monkeypatch):
    seen: list[str] = []

    async def handler(request):
        seen.append(str(request.url))
        return httpx.Response(302, headers={"Location": "https://evil.example/userinfo"})

    install_userinfo(monkeypatch, handler)
    assert await mcp.validate_identity_hub_token("redirect-sentinel") is None
    assert seen == [mcp._USERINFO_URL]


@pytest.mark.parametrize(
    "failure",
    [
        httpx.ReadTimeout("timeout"),
        httpx.ConnectError("network"),
    ],
)
async def test_userinfo_network_failures_are_redacted(monkeypatch, failure, loguru_sink):
    token = "network-sentinel"

    async def handler(request):
        raise failure

    install_userinfo(monkeypatch, handler)
    assert await mcp.validate_identity_hub_token(token) is None
    assert token not in loguru_sink.getvalue()
    assert token not in repr(failure)


async def test_userinfo_stall_fails_closed_within_deadline(monkeypatch):
    monkeypatch.setattr(mcp, "_USERINFO_DEADLINE", 0.2)

    async def handler(request):
        await asyncio.sleep(10)
        return httpx.Response(200, json={"sub": "never"})

    install_userinfo(monkeypatch, handler)
    started = time.monotonic()
    assert (
        await asyncio.wait_for(mcp.validate_identity_hub_token("stall-sentinel"), timeout=3) is None
    )
    assert time.monotonic() - started < 2


@pytest.mark.parametrize(
    "response_factory",
    [
        lambda: httpx.Response(200, content=b"not-json"),
        lambda: httpx.Response(200, json={}),
        lambda: httpx.Response(200, json={"sub": ""}),
        lambda: httpx.Response(200, json={"sub": " "}),
        lambda: httpx.Response(200, json=[]),
        lambda: httpx.Response(200, content=b'{"sub": "' + b"a" * 70000 + b'"}'),
    ],
)
async def test_userinfo_malformed_responses_fail_closed(monkeypatch, response_factory):
    async def handler(request):
        return response_factory()

    install_userinfo(monkeypatch, handler)
    assert await mcp.validate_identity_hub_token("malformed-sentinel") is None


async def test_userinfo_valid_subject_is_returned(monkeypatch):
    async def handler(request):
        return httpx.Response(200, json={"sub": "subject-1"})

    install_userinfo(monkeypatch, handler)
    assert await mcp.validate_identity_hub_token("valid-sentinel") == "subject-1"


async def test_positive_result_is_cached_within_ttl(monkeypatch):
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"sub": "subject-1"})

    install_userinfo(monkeypatch, handler)
    for _ in range(5):
        assert await mcp.validate_identity_hub_token("cache-sentinel") == "subject-1"
    assert calls == 1


async def test_cache_expiry_revalidates(monkeypatch):
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"sub": f"subject-{calls}"})

    install_userinfo(monkeypatch, handler)
    monkeypatch.setattr(mcp, "_POSITIVE_TTL", 0.0)
    assert await mcp.validate_identity_hub_token("expiry-sentinel") == "subject-1"
    assert await mcp.validate_identity_hub_token("expiry-sentinel") == "subject-2"
    assert calls == 2


async def test_cache_evicts_oldest_beyond_max(monkeypatch):
    async def handler(request):
        return httpx.Response(200, json={"sub": "subject"})

    install_userinfo(monkeypatch, handler)
    monkeypatch.setattr(mcp, "_CACHE_MAX_ENTRIES", 2)
    for token in ("aaa", "bbb", "ccc"):
        await mcp.validate_identity_hub_token(token)
    assert len(mcp._validation_cache) == 2
    assert mcp._token_digest("aaa") not in mcp._validation_cache
    assert mcp._token_digest("ccc") in mcp._validation_cache


async def test_cache_never_stores_raw_tokens(monkeypatch):
    async def handler(request):
        return httpx.Response(200, json={"sub": "subject"})

    install_userinfo(monkeypatch, handler)
    token = "raw-token-sentinel"
    await mcp.validate_identity_hub_token(token)
    assert token not in repr(mcp._validation_cache)
    assert all(token not in key for key in mcp._validation_cache)


def test_token_digest_is_salted_and_not_plain_sha256():
    import hashlib

    token = "digest-sentinel"
    assert mcp._token_digest(token) != hashlib.sha256(token.encode()).hexdigest()
    assert mcp._token_digest(token) == mcp._token_digest(token)


async def test_failures_use_short_negative_ttl(monkeypatch):
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(401)

    install_userinfo(monkeypatch, handler)
    assert mcp._NEGATIVE_TTL <= mcp._POSITIVE_TTL
    await mcp.validate_identity_hub_token("negative-sentinel")
    monkeypatch.setattr(mcp, "_NEGATIVE_TTL", 0.0)
    await mcp.reset_validation_cache()
    monkeypatch.setattr(mcp, "_validation_shutting_down", False)
    await mcp.validate_identity_hub_token("negative-sentinel")
    await mcp.validate_identity_hub_token("negative-sentinel")
    assert calls == 3


async def test_concurrent_validations_are_bounded(monkeypatch):
    monkeypatch.setattr(mcp, "_userinfo_gate", asyncio.Semaphore(2))
    in_flight = 0
    peak = 0

    async def handler(request):
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)
        in_flight -= 1
        return httpx.Response(200, json={"sub": "subject"})

    install_userinfo(monkeypatch, handler)
    await asyncio.wait_for(
        asyncio.gather(
            *(mcp.validate_identity_hub_token(f"bounded-{index}") for index in range(8))
        ),
        timeout=5,
    )
    assert peak <= 2


async def test_verifier_rejects_syntax_before_userinfo():
    called = False

    async def validator(token):
        nonlocal called
        called = True
        return "subject"

    verifier = mcp.YandexBearerVerifier(validator)
    assert await verifier.verify_token("bad token") is None
    assert called is False


async def test_verifier_rejects_oversized_bearer():
    called = False

    async def validator(token):
        nonlocal called
        called = True
        return "subject"

    verifier = mcp.YandexBearerVerifier(validator)
    assert await verifier.verify_token("a" * (mcp.MAX_BEARER_LENGTH + 1)) is None
    assert called is False


async def test_verifier_returns_authenticated_identity():
    verifier = mcp.YandexBearerVerifier(lambda token: _subject(token))
    access_token = await verifier.verify_token("valid-token")
    assert access_token is not None
    assert access_token.token == "valid-token"
    assert access_token.subject == "subject-valid-token"


async def _subject(token):
    return f"subject-{token}"
