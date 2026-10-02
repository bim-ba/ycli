"""OAuthClient — device/implicit OAuth HTTP + api360 org lookup (stubbed with responses)."""

import httpx2
import pytest

from ycli.yandex.errors import (
    YandexAuthError,
    YandexClientError,
    YandexConnectionError,
    YandexServerError,
)
from ycli.yandex.status.client import OAuthClient

DEVICE_CODE_URL = "https://oauth.yandex.ru/device/code"
TOKEN_URL = "https://oauth.yandex.ru/token"
ORG_URL = "https://api360.yandex.net/directory/v1/org"


def _client():
    return OAuthClient(client_id="id", client_secret="secret", timeout_seconds=30.0, retries=3)


def test_authorize_url_carries_client_id():
    url = OAuthClient(client_id="my-app", timeout_seconds=30.0, retries=3).authorize_url()
    assert url == "https://oauth.yandex.ru/authorize?response_type=token&client_id=my-app"


def test_request_device_code_parses_response(api):
    api.add(
        "POST",
        DEVICE_CODE_URL,
        json={
            "device_code": "dev-123",
            "user_code": "ABCD-EFGH",
            "verification_url": "https://ya.ru/device",
            "expires_in": 300,
            "interval": 5,
        },
        status=200,
    )
    device = _client().request_device_code()
    assert device.device_code == "dev-123"
    assert device.user_code == "ABCD-EFGH"
    assert device.verification_url == "https://ya.ru/device"
    assert device.interval == 5


def test_request_device_code_sends_device_name(api):
    api.add("POST", DEVICE_CODE_URL, json={"device_code": "d"}, status=200)
    _client().request_device_code(device_name="my-laptop")
    assert "device_name=my-laptop" in api.calls[0].content.decode()


def test_poll_token_success(api):
    api.add(
        "POST",
        TOKEN_URL,
        json={"access_token": "tok-abc", "token_type": "bearer", "expires_in": 3600},
        status=200,
    )
    result = _client().poll_token("dev-123")
    assert result.pending is False
    assert result.error == ""
    assert result.token is not None
    assert result.token.access_token == "tok-abc"


def test_poll_token_pending(api):
    api.add("POST", TOKEN_URL, json={"error": "authorization_pending"}, status=400)
    result = _client().poll_token("dev-123")
    assert result.token is None
    assert result.pending is True
    assert result.error == ""


def test_poll_token_terminal_error(api):
    api.add("POST", TOKEN_URL, json={"error": "invalid_client"}, status=400)
    result = _client().poll_token("dev-123")
    assert result.token is None
    assert result.pending is False
    assert result.error == "invalid_client"


def test_poll_token_invalid_client_as_401_is_a_polling_state(api):
    # RFC 6749 §5.2: invalid_client MAY come back as 401 instead of 400.
    api.add("POST", TOKEN_URL, json={"error": "invalid_client"}, status=401)
    assert _client().poll_token("dev-123").error == "invalid_client"


@pytest.mark.parametrize(
    ("status", "body", "error"),
    [
        (400, "{}", YandexClientError),  # a 400 without an OAuth error code is no polling state
        (400, "<html>Bad Request</html>", YandexClientError),
        (403, '{"error": "forbidden"}', YandexAuthError),  # not an OAuth token-endpoint status
        (503, "<html>Service Unavailable</html>", YandexServerError),
    ],
)
def test_poll_token_maps_other_failures_to_typed_errors(api, status, body, error):
    api.add("POST", TOKEN_URL, content=body, status=status)
    with pytest.raises(error) as raised:
        _client().poll_token("dev-123")
    assert raised.value.status == status


@pytest.mark.parametrize(
    ("status", "body", "error"),
    [
        (400, '{"error": "invalid_client"}', YandexClientError),
        (503, "<html>Service Unavailable</html>", YandexServerError),
    ],
)
def test_request_device_code_maps_failures_to_typed_errors(api, status, body, error):
    api.add("POST", DEVICE_CODE_URL, content=body, status=status)
    with pytest.raises(error, match=f"{status} .* for POST {DEVICE_CODE_URL}"):
        _client().request_device_code()


def test_fetch_organizations_returns_list(api):
    api.add(
        "GET",
        ORG_URL,
        json={"organizations": [{"id": 1, "name": "Acme"}, {"id": 2, "name": "Beta"}]},
        status=200,
    )
    orgs = _client().fetch_organizations("tok")
    assert [o.id for o in orgs] == [1, 2]
    assert orgs[0].name == "Acme"
    # Authorization: OAuth scheme reused from transport
    assert api.calls[0].headers["Authorization"] == "OAuth tok"


def test_fetch_organizations_empty_on_missing_scope(api):
    api.add("GET", ORG_URL, json={"code": 7, "message": "No required scope"}, status=403)
    assert _client().fetch_organizations("tok") == []


def test_fetch_organizations_empty_on_rejected_token(api):
    api.add("GET", ORG_URL, json={"message": "Unauthorized"}, status=401)
    assert _client().fetch_organizations("tok") == []


@pytest.mark.parametrize(
    ("status", "body", "error"),
    [
        (400, '{"message": "bad request"}', YandexClientError),
        (503, "<html>Service Unavailable</html>", YandexServerError),
    ],
)
def test_fetch_organizations_raises_on_other_failures(api, status, body, error):
    """Only 401/403 mean "no directory scope"; any other failure is not an empty org list."""
    api.add("GET", ORG_URL, content=body, status=status)
    with pytest.raises(error):
        OAuthClient(client_id="id", timeout_seconds=30.0, retries=0).fetch_organizations("tok")


def _drop(request):
    raise httpx2.ConnectError("connection refused", request=request)


def test_a_lost_connection_is_a_typed_error(monkeypatch):
    monkeypatch.setattr(
        "ycli.yandex.core.session.default_transport", lambda: httpx2.MockTransport(_drop)
    )
    with pytest.raises(YandexConnectionError, match="ConnectError"):
        _client().request_device_code()
