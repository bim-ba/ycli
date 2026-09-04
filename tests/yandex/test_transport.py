"""TDD for the Yandex Transport — the single auth boundary.

Transport.session(*, oauth_token, organization_id, timeout_seconds, retries, base) is PURE:
it never reads os.environ. It returns a requests.Session with OAuth + a single canonical org
header (X-Org-Id; header names are case-insensitive per RFC 9110, so one casing serves
Wiki/Tracker/Forms), a urllib3 Retry adapter on idempotent methods only, and a default
timeout. Empty args raise. When base is supplied, that session is configured in place and
returned instead of a fresh one.
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests
import responses

from ycli.yandex.auth import ServiceAccountCredentials
from ycli.yandex.transport import Transport


def test_session_sets_auth_and_org_headers():
    s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    assert s.headers["Authorization"] == "OAuth t"
    assert s.headers["X-Org-Id"] == "o"


def test_session_sets_static_iam_and_cloud_org_headers():
    session = Transport.session(iam_token="iam", cloud_organization_id="cloud")
    assert session.headers["Authorization"] == "Bearer iam"
    assert session.headers["X-Cloud-Org-Id"] == "cloud"
    assert "X-Org-Id" not in session.headers


def test_oauth_precedes_static_iam():
    session = Transport.session(
        oauth_token="oauth", iam_token="iam", cloud_organization_id="cloud"
    )
    assert session.headers["Authorization"] == "OAuth oauth"


def test_iam_requires_cloud_organization():
    with pytest.raises(ValueError, match="cloud_organization_id"):
        Transport.session(iam_token="iam", organization_id="org")


def test_two_organization_ids_raise():
    with pytest.raises(ValueError, match="exactly one"):
        Transport.session(
            oauth_token="oauth", organization_id="org", cloud_organization_id="cloud"
        )


def test_session_applies_configured_timeout_and_retries():
    s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=12.5, retries=7)
    adapter = s.get_adapter("https://example.com")
    assert adapter._timeout == 12.5  # ty: ignore[unresolved-attribute]
    assert adapter.max_retries.total == 7  # ty: ignore[unresolved-attribute]


def test_session_rejects_empty_credentials():
    with pytest.raises(ValueError, match="token"):
        Transport.session(oauth_token="", organization_id="o", timeout_seconds=30.0, retries=3)


def test_empty_org_raises():
    with pytest.raises(ValueError, match="organization_id"):
        Transport.session(oauth_token="t", organization_id="", timeout_seconds=30.0, retries=3)


def test_session_carries_auth_and_org_headers():
    s = Transport.session(oauth_token="tok", organization_id="org", timeout_seconds=30.0, retries=3)
    assert isinstance(s, requests.Session)
    assert s.headers["Authorization"] == "OAuth tok"
    assert s.headers["X-Org-Id"] == "org"


def test_session_mounts_retry_adapter_on_https():
    s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    adapter = s.get_adapter("https://api.wiki.yandex.net/v1/pages")
    assert adapter.max_retries.total == 3  # ty: ignore[unresolved-attribute]
    assert 429 in adapter.max_retries.status_forcelist  # ty: ignore[unresolved-attribute]
    assert 500 in adapter.max_retries.status_forcelist  # ty: ignore[unresolved-attribute]


def test_post_not_retried_only_idempotent_methods():
    s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    adapter = s.get_adapter("https://api.wiki.yandex.net/v1/pages")
    methods = adapter.max_retries.allowed_methods  # ty: ignore[unresolved-attribute]
    assert "POST" not in methods
    assert "GET" in methods


def test_session_does_not_read_environment(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "should-be-ignored")
    s = Transport.session(
        oauth_token="explicit", organization_id="o", timeout_seconds=30.0, retries=3
    )
    assert s.headers["Authorization"] == "OAuth explicit"


def test_timeout_adapter_injects_default_when_none(monkeypatch):
    # responses mounts its own adapter and bypasses _TimeoutAdapter.send;
    # unit-test send() directly.
    from ycli.yandex.transport import _TimeoutAdapter

    captured: dict[str, object] = {}

    def fake_send(self, request, **kwargs):
        captured.update(kwargs)
        return requests.Response()

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", fake_send)  # ty: ignore[possibly-missing-submodule]
    adapter = _TimeoutAdapter(timeout=12.5)
    prepared = requests.Request("GET", "https://example.com").prepare()

    adapter.send(prepared)
    assert captured["timeout"] == 12.5


def test_timeout_adapter_passes_explicit_timeout_through(monkeypatch):
    from ycli.yandex.transport import _TimeoutAdapter

    captured: dict[str, object] = {}

    def fake_send(self, request, **kwargs):
        captured.update(kwargs)
        return requests.Response()

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", fake_send)  # ty: ignore[possibly-missing-submodule]
    adapter = _TimeoutAdapter(timeout=12.5)
    prepared = requests.Request("GET", "https://example.com").prepare()

    adapter.send(prepared, timeout=3.0)
    assert captured["timeout"] == 3.0


def test_no_hardcoded_uplink_timeout_in_clients():
    src = Path(__file__).resolve().parents[2] / "src" / "ycli" / "yandex"
    offenders = [str(p) for p in src.rglob("client.py") if "@uplink.timeout" in p.read_text()]
    assert not offenders, offenders


def test_session_configures_a_supplied_bare_base():
    from ycli.yandex.transport import _TimeoutAdapter

    bare = requests.Session()
    out = Transport.session(oauth_token="t", organization_id="o", base=bare)
    assert out is bare  # configured in place, not replaced
    assert out.headers["Authorization"] == "OAuth t"
    assert out.headers["X-Org-Id"] == "o"
    assert Transport._raise_typed in out.hooks["response"]
    assert isinstance(out.get_adapter("https://example.com"), _TimeoutAdapter)


def test_session_clears_stale_headers_on_supplied_base():
    bare = requests.Session()
    bare.headers.update(
        {"Authorization": "stale", "X-Org-Id": "old", "X-Cloud-Org-Id": "old-cloud"}
    )
    out = Transport.session(iam_token="iam", cloud_organization_id="cloud", base=bare)
    assert out.headers["Authorization"] == "Bearer iam"
    assert out.headers["X-Cloud-Org-Id"] == "cloud"
    assert "X-Org-Id" not in out.headers


def test_response_hook_is_registered():
    s = Transport.session(oauth_token="t", organization_id="o")
    assert Transport._raise_typed in s.hooks["response"]


def test_authorization_header_uses_oauth_scheme():
    assert Transport._authorization("abc") == "OAuth abc"
    assert Transport._authorization(iam_token="abc") == "Bearer abc"
    assert Transport._authorization() is None


def test_service_account_auth_applies_generated_token(monkeypatch):
    from ycli.yandex.transport import _ServiceAccountTokenProvider

    sdk = Mock()
    sdk.client.return_value = Mock()
    monkeypatch.setattr("ycli.yandex.transport.yandexcloud.SDK", Mock(return_value=sdk))
    monkeypatch.setattr(_ServiceAccountTokenProvider, "get_token", lambda self: "generated")
    credentials = ServiceAccountCredentials("key", "account", "private")
    session = Transport.session(
        service_account=credentials, cloud_organization_id="cloud"
    )
    prepared = session.prepare_request(requests.Request("GET", "https://example.com"))
    assert prepared.headers["Authorization"] == "Bearer generated"


def test_service_account_provider_builds_jwt_and_caches(monkeypatch):
    from ycli.yandex.transport import _ServiceAccountTokenProvider

    response = SimpleNamespace(
        iam_token="generated",
        expires_at=SimpleNamespace(
            ToDatetime=lambda *, tzinfo: datetime.now(tzinfo) + timedelta(hours=12)
        ),
    )
    iam_service = Mock()
    iam_service.Create.return_value = response
    sdk = Mock()
    sdk.client.return_value = iam_service
    sdk_factory = Mock(return_value=sdk)
    encode = Mock(return_value="encoded")
    monkeypatch.setattr("ycli.yandex.transport.yandexcloud.SDK", sdk_factory)
    monkeypatch.setattr("ycli.yandex.transport.jwt.encode", encode)
    monkeypatch.setattr("ycli.yandex.transport.time.time", lambda: 1000)

    credentials = ServiceAccountCredentials("key", "account", "private")
    provider = _ServiceAccountTokenProvider(credentials)
    assert provider.get_token() == "generated"
    assert provider.get_token() == "generated"

    sdk_factory.assert_called_once_with(service_account_key=credentials.to_yandexcloud_dict())
    sdk.client.assert_called_once()
    encode.assert_called_once_with(
        {
            "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
            "iss": "account",
            "iat": 1000,
            "exp": 4600,
        },
        "private",
        algorithm="PS256",
        headers={"kid": "key"},
    )
    request = iam_service.Create.call_args.args[0]
    assert request.jwt == "encoded"


def test_service_account_provider_refreshes_expired_token(monkeypatch):
    from ycli.yandex.transport import _ServiceAccountTokenProvider

    iam_service = Mock()
    iam_service.Create.side_effect = [
        SimpleNamespace(iam_token="first"),
        SimpleNamespace(iam_token="second"),
    ]
    sdk = Mock()
    sdk.client.return_value = iam_service
    monkeypatch.setattr("ycli.yandex.transport.yandexcloud.SDK", Mock(return_value=sdk))
    monkeypatch.setattr("ycli.yandex.transport.jwt.encode", Mock(return_value="encoded"))
    provider = _ServiceAccountTokenProvider(
        ServiceAccountCredentials("key", "account", "private")
    )
    assert provider.get_token() == "first"
    provider._refresh_at = datetime.now(UTC) - timedelta(seconds=1)
    assert provider.get_token() == "second"
    assert iam_service.Create.call_count == 2


def test_service_account_provider_rechecks_cache_inside_lock(monkeypatch):
    from ycli.yandex.transport import _ServiceAccountTokenProvider

    sdk = Mock()
    sdk.client.return_value = Mock()
    monkeypatch.setattr("ycli.yandex.transport.yandexcloud.SDK", Mock(return_value=sdk))
    provider = _ServiceAccountTokenProvider(
        ServiceAccountCredentials("key", "account", "private")
    )

    class PopulateCache:
        def __enter__(self):
            provider._token = "concurrent"
            provider._refresh_at = datetime.now(UTC) + timedelta(minutes=1)

        def __exit__(self, *args):
            return None

    provider._lock = PopulateCache()  # ty: ignore[invalid-assignment]
    assert provider.get_token() == "concurrent"


def test_service_account_requires_cloud_organization(monkeypatch):
    sdk = Mock()
    sdk.client.return_value = Mock()
    monkeypatch.setattr("ycli.yandex.transport.yandexcloud.SDK", Mock(return_value=sdk))
    with pytest.raises(ValueError, match="service-account IAM requires"):
        Transport.session(
            service_account=ServiceAccountCredentials("key", "account", "private"),
            organization_id="org",
        )


def test_service_account_auth_is_tracker_only(monkeypatch):
    from ycli.yandex.forms.client import FormsClient
    from ycli.yandex.tracker.client import TrackerClient
    from ycli.yandex.wiki.client import WikiClient

    sdk = Mock()
    sdk.client.return_value = Mock()
    monkeypatch.setattr("ycli.yandex.transport.yandexcloud.SDK", Mock(return_value=sdk))
    credentials = ServiceAccountCredentials("key", "account", "private")

    tracker = TrackerClient(service_account=credentials, cloud_organization_id="cloud")
    assert tracker.me._session.auth is not None
    for client_class in (WikiClient, FormsClient):
        with pytest.raises(ValueError, match="only by Tracker"):
            client_class(service_account=credentials, cloud_organization_id="cloud")


def test_oauth_precedence_allows_service_account_fallback_on_wiki():
    from ycli.yandex.wiki.client import WikiClient

    client = WikiClient(
        oauth_token="oauth",
        service_account=ServiceAccountCredentials("key", "account", "private"),
        cloud_organization_id="cloud",
    )
    assert client.me._session.headers["Authorization"] == "OAuth oauth"


@responses.activate
def test_client_honors_configured_timeout_not_hardcoded(monkeypatch):
    """Timeout from _TimeoutAdapter reaches the request; no per-method override interferes."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    monkeypatch.setenv("YCLI_TIMEOUT_SECONDS", "99")
    from ycli.yandex.transport import _TimeoutAdapter

    seen: dict = {}
    real_send = _TimeoutAdapter.send

    def spy(self, request, **kw):
        seen["incoming_timeout"] = kw.get("timeout")
        seen["adapter_timeout"] = self._timeout
        return real_send(self, request, **kw)

    monkeypatch.setattr(_TimeoutAdapter, "send", spy)
    responses.add(
        responses.GET, "https://api.tracker.yandex.net/v3/priorities", json=[], status=200
    )
    from ycli.yandex.tracker.dependencies import tracker_client

    tracker_client().priorities.list()
    assert seen["incoming_timeout"] is None, f"Expected None but got {seen['incoming_timeout']}"
    assert seen["adapter_timeout"] == 99.0, f"Expected 99.0 but got {seen['adapter_timeout']}"
