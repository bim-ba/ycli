"""OAuthClient — device/implicit OAuth HTTP + api360 org lookup (stubbed with responses)."""

import responses

from ycli.yandex.status.client import OAuthClient

DEVICE_CODE_URL = "https://oauth.yandex.ru/device/code"
TOKEN_URL = "https://oauth.yandex.ru/token"
ORG_URL = "https://api360.yandex.net/directory/v1/org"


def _client():
    return OAuthClient(client_id="id", client_secret="secret")


def test_authorize_url_carries_client_id():
    url = OAuthClient(client_id="my-app").authorize_url()
    assert url == "https://oauth.yandex.ru/authorize?response_type=token&client_id=my-app"


@responses.activate
def test_request_device_code_parses_response():
    responses.add(
        responses.POST,
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


@responses.activate
def test_request_device_code_sends_device_name():
    responses.add(responses.POST, DEVICE_CODE_URL, json={"device_code": "d"}, status=200)
    _client().request_device_code(device_name="my-laptop")
    assert "device_name=my-laptop" in str(responses.calls[0].request.body)


@responses.activate
def test_poll_token_success():
    responses.add(
        responses.POST,
        TOKEN_URL,
        json={"access_token": "tok-abc", "token_type": "bearer", "expires_in": 3600},
        status=200,
    )
    result = _client().poll_token("dev-123")
    assert result.pending is False
    assert result.error == ""
    assert result.token is not None
    assert result.token.access_token == "tok-abc"


@responses.activate
def test_poll_token_pending():
    responses.add(responses.POST, TOKEN_URL, json={"error": "authorization_pending"}, status=400)
    result = _client().poll_token("dev-123")
    assert result.token is None
    assert result.pending is True
    assert result.error == ""


@responses.activate
def test_poll_token_terminal_error():
    responses.add(responses.POST, TOKEN_URL, json={"error": "invalid_client"}, status=400)
    result = _client().poll_token("dev-123")
    assert result.token is None
    assert result.pending is False
    assert result.error == "invalid_client"


@responses.activate
def test_poll_token_error_without_field_uses_fallback():
    responses.add(responses.POST, TOKEN_URL, json={}, status=400)
    result = _client().poll_token("dev-123")
    assert result.error == "authorization failed"


@responses.activate
def test_fetch_organizations_returns_list():
    responses.add(
        responses.GET,
        ORG_URL,
        json={"organizations": [{"id": 1, "name": "Acme"}, {"id": 2, "name": "Beta"}]},
        status=200,
    )
    orgs = _client().fetch_organizations("tok")
    assert [o.id for o in orgs] == [1, 2]
    assert orgs[0].name == "Acme"
    # Authorization: OAuth scheme reused from transport
    assert responses.calls[0].request.headers["Authorization"] == "OAuth tok"


@responses.activate
def test_fetch_organizations_empty_on_missing_scope():
    responses.add(
        responses.GET, ORG_URL, json={"code": 7, "message": "No required scope"}, status=403
    )
    assert _client().fetch_organizations("tok") == []
