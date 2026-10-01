"""SyncSession / AsyncSession: typed errors, retries by effect, logging, page walking."""

import logging

import httpx2
import pytest
from pydantic import SecretStr

from tests.mock_api import MockAPI
from ycli.settings import HTTPConfig
from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.core.pagination import PageNumberPagination
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.core.session import connect, connect_async, default_transport
from ycli.yandex.errors import (
    YandexAuthError,
    YandexConnectionError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
)

PROFILE = ServiceProfile("https://api.test/v1")
URL = "https://api.test/v1/items"


def _session(api: MockAPI, retries: int = 2):
    return connect(
        PROFILE,
        auth=OAuthTokenAuth(SecretStr("y0_secret")),
        organization_id="org",
        http=HTTPConfig(retries=retries),
        transport=api.transport(),
    )


def _listing() -> Paged[list[int], int]:
    return Paged(Endpoint("GET", "items", list[int]), PageNumberPagination(page_size=2), list)


def test_send_applies_base_url_auth_and_org_header():
    api = MockAPI()
    api.add("GET", URL, json=[1])
    assert _session(api).send(Endpoint("GET", "items", list[int])) == [1]
    request = api.calls[0]
    assert request.headers["Authorization"] == "OAuth y0_secret"
    assert request.headers["X-Org-Id"] == "org"


@pytest.mark.parametrize(
    ("status", "error"),
    [(401, YandexAuthError), (404, YandexNotFoundError), (500, YandexServerError)],
)
def test_non_2xx_raises_the_typed_error_with_the_api_message(status, error):
    api = MockAPI()
    api.add("GET", URL, json={"errorMessages": ["Nope."]}, status=status)
    with pytest.raises(error, match=r"Nope\."):
        _session(api, retries=0).send(Endpoint("GET", "items"))


def test_a_5xx_is_retried_for_a_read():
    api = MockAPI()
    api.add("GET", URL, status=503)
    api.add("GET", URL, json=[1])
    assert _session(api).send(Endpoint("GET", "items", list[int])) == [1]
    assert len(api.calls) == 2


def test_a_5xx_is_not_retried_for_a_create():
    api = MockAPI()
    api.add("POST", URL, status=503)
    with pytest.raises(YandexServerError):
        _session(api).send(Endpoint("POST", "items"))
    assert len(api.calls) == 1


def test_a_429_is_retried_even_for_a_create_and_reads_retry_after(caplog):
    api = MockAPI()
    api.add("POST", URL, status=429, headers={"Retry-After": "0"})
    api.add("POST", URL, status=429, headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"})
    api.add("POST", URL, json={"id": 1})
    caplog.set_level(logging.INFO, logger="ycli.http")
    assert _session(api).send(Endpoint("POST", "items", dict)) == {"id": 1}
    assert len(api.calls) == 3
    assert "retrying POST https://api.test/v1/items (attempt 2 of 3)" in caplog.text


def test_retries_run_out():
    api = MockAPI()
    api.add("GET", URL, status=429, headers={"Retry-After": "0"})
    with pytest.raises(YandexRateLimitError) as caught:
        _session(api, retries=1).send(Endpoint("GET", "items"))
    assert caught.value.retry_after == 0.0
    assert len(api.calls) == 2


def _drop(request: httpx2.Request) -> httpx2.Response:
    raise httpx2.ConnectError("connection refused", request=request)


def test_a_lost_connection_is_a_typed_error():
    session = connect(
        PROFILE, auth=OAuthTokenAuth(SecretStr("t")), transport=httpx2.MockTransport(_drop)
    )
    with pytest.raises(YandexConnectionError, match="connection refused"):
        session.send(Endpoint("GET", "items"))


def test_each_request_is_logged_without_secrets(caplog):
    api = MockAPI()
    api.add("GET", URL, json=[])
    caplog.set_level(logging.INFO, logger="ycli.http")
    _session(api).send(Endpoint("GET", "items"))
    assert "GET https://api.test/v1/items -> 200" in caplog.text
    assert "y0_secret" not in caplog.text


def test_iterate_walks_pages_until_a_short_one():
    api = MockAPI()
    api.add("GET", URL, json=[1, 2])
    api.add("GET", URL, json=[3])
    assert list(_session(api).iterate(_listing())) == [1, 2, 3]


def test_iterate_stops_on_an_empty_page():
    api = MockAPI()
    api.add("GET", URL, json=[])
    assert list(_session(api).iterate(_listing())) == []


def test_iterate_stops_after_max_pages(caplog):
    api = MockAPI()
    api.add("GET", URL, json=[1, 2])  # every page is full, so the walk never ends by itself
    assert list(_session(api).iterate(_listing(), max_pages=3)) == [1, 2] * 3
    assert "stopped after 3 pages" in caplog.text


@pytest.mark.parametrize(("limit", "fetched"), [(1, 1), (2, 1), (3, 2)])
def test_iterate_warns_when_the_limit_leaves_items(caplog, limit, fetched):
    api = MockAPI()
    api.add("GET", URL, json=[1, 2])
    assert list(_session(api).iterate(_listing(), limit=limit)) == [1, 2, 1][:limit]
    assert len(api.calls) == fetched
    assert f"stopped at {limit} items" in caplog.text


def test_iterate_at_an_exact_end_does_not_warn(caplog):
    api = MockAPI()
    api.add("GET", URL, json=[1])
    assert list(_session(api).iterate(_listing(), limit=1)) == [1]
    assert "stopped at" not in caplog.text


def test_close_closes_the_client():
    session = _session(MockAPI())
    session.close()
    assert session._client.is_closed


async def test_async_session_mirrors_the_sync_contract(caplog):
    api = MockAPI()
    api.add("GET", URL, status=503)
    api.add("GET", URL, json=[1, 2])
    api.add("GET", URL, json=[3])
    session = connect_async(
        PROFILE,
        auth=OAuthTokenAuth(SecretStr("t")),
        http=HTTPConfig(retries=1),
        transport=api.transport(),
    )
    assert await session.send(Endpoint("GET", "items", list[int])) == [1, 2]
    assert [item async for item in session.iterate(_listing())] == [3]
    with pytest.raises(YandexServerError):
        api.add("GET", f"{URL}/broken", status=500)
        await session.send(Endpoint("GET", "items/broken"))
    await session.aclose()


async def test_async_iterate_limits_and_page_cap(caplog):
    api = MockAPI()
    api.add("GET", URL, json=[1, 2])
    session = connect_async(PROFILE, auth=OAuthTokenAuth(SecretStr("t")), transport=api.transport())
    assert [item async for item in session.iterate(_listing(), limit=3)] == [1, 2, 1]
    assert [item async for item in session.iterate(_listing(), max_pages=1)] == [1, 2]
    assert "stopped after 1 pages" in caplog.text


async def test_async_lost_connection_is_typed():
    session = connect_async(
        PROFILE, auth=OAuthTokenAuth(SecretStr("t")), transport=httpx2.MockTransport(_drop)
    )
    with pytest.raises(YandexConnectionError):
        await session.send(Endpoint("GET", "items"))


def test_the_default_transport_is_httpx2s_own():
    """Bound at import, before the autouse fixture swaps the seam for an offline one."""
    assert default_transport() is None


def test_the_retry_policy_waits_as_long_as_retry_after_says():
    from ycli.yandex.core.session import _retry_policy

    decide = _retry_policy(idempotent=False)
    assert decide(YandexRateLimitError("slow down", retry_after=7.0)) == 7.0
    assert decide(YandexRateLimitError("slow down")) is True
    assert decide(YandexServerError("boom")) is False
    assert _retry_policy(idempotent=True)(YandexServerError("boom")) is True


def test_a_redirect_is_followed():
    api = MockAPI()
    api.add("GET", f"{URL}/OLD-1", status=301, headers={"Location": f"{URL}/NEW-1"})
    api.add("GET", f"{URL}/NEW-1", json={"key": "NEW-1"})
    assert _session(api).send(Endpoint("GET", "items/OLD-1", dict)) == {"key": "NEW-1"}


def test_a_retry_after_beyond_the_cap_fails_fast():
    api = MockAPI()
    api.add("GET", URL, status=429, headers={"Retry-After": "86400"})
    with pytest.raises(YandexRateLimitError) as caught:
        _session(api).send(Endpoint("GET", "items"))
    assert caught.value.retry_after == 86400.0
    assert len(api.calls) == 1


@pytest.mark.parametrize("value", ["-1", "nan", "inf", "Wed, 21 Oct 2026 07:28:00 GMT"])
def test_a_retry_after_that_is_not_a_delay_is_ignored(value):
    api = MockAPI()
    api.add("GET", URL, status=429, headers={"Retry-After": value})
    api.add("GET", URL, json=[1])
    assert _session(api).send(Endpoint("GET", "items", list[int])) == [1]


def test_secret_query_parameters_are_masked_in_logs_and_errors(caplog):
    api = MockAPI()
    api.add("GET", URL, status=404, json={"message": "nope"})
    caplog.set_level(logging.INFO, logger="ycli.http")
    endpoint = Endpoint("GET", "items", params={"apikey": "TOPSECRET", "lang": "ru"})
    with pytest.raises(YandexNotFoundError) as caught:
        _session(api).send(endpoint)
    assert "TOPSECRET" not in str(caught.value)
    assert "TOPSECRET" not in (caught.value.url or "")
    assert "TOPSECRET" not in caplog.text
    assert "lang=ru" in caplog.text


def test_connect_async_uses_the_transport_seam():
    session = connect_async(PROFILE, auth=OAuthTokenAuth(SecretStr("t")))
    assert isinstance(session._client._transport, httpx2.MockTransport)
