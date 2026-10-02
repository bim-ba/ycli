"""OAuth device/implicit login HTTP — the ONLY place this feature does HTTP (ARCH-2).

Deliberately does NOT use ``Transport.session``: the device poll legitimately returns
HTTP 400 ``authorization_pending`` until the user approves, and Transport installs a
raise-on-4xx hook that would turn that expected 400 into an exception. So this builds a
plain ``requests.Session`` and maps every other failure through ``errors.error_for_status``
itself, reusing transport's ``_TimeoutAdapter`` for a bounded timeout and its
``Authorization: OAuth`` scheme for the api360 org lookup. Credentials (the user's own client
id/secret) arrive as constructor arguments — this never reads the environment (ARCH-7).
"""

from __future__ import annotations

from dataclasses import dataclass

import requests

from ycli.yandex.errors import YandexAuthError, describe_error_body, error_for_status
from ycli.yandex.status.oauth_models import (
    DeviceCodeResponse,
    Organization,
    OrganizationList,
    TokenResponse,
)
from ycli.yandex.transport import Transport, _TimeoutAdapter, log_response, retry_policy

# RFC 6749 §5.2: the token endpoint answers an OAuth error with 400, or 401 for invalid_client.
_OAUTH_ERROR_STATUSES = frozenset({400, 401})


def _raise_for_error(response: requests.Response) -> None:
    """Raise the typed ``YandexError`` for a non-2xx ``response``, worded like the transport's.

    A 2xx returns ``None``; a 503 HTML page raises ``YandexServerError("503 Service
    Unavailable for POST https://oauth.yandex.ru/device/code: <html>…")``.
    """
    code = response.status_code
    if code < 400:
        return
    detail = describe_error_body(response.text)
    message = f"{code} {response.reason} for {response.request.method} {response.url}: {detail}"
    raise error_for_status(code, message, url=response.url)


def _oauth_error(response: requests.Response) -> str:
    """The OAuth ``error`` code of a token-endpoint answer, or ``""`` if it carries none.

    A 400 ``{"error": "authorization_pending"}`` gives ``"authorization_pending"``; a 200, a
    503 or a 400 HTML page gives ``""``.
    """
    if response.status_code not in _OAUTH_ERROR_STATUSES:
        return ""
    try:
        body = response.json()
    except requests.JSONDecodeError:
        return ""
    error = body.get("error") if isinstance(body, dict) else None
    return error if isinstance(error, str) else ""


@dataclass(frozen=True)
class TokenPollResult:
    """One device-token poll outcome: a token, still-pending, or a terminal error."""

    token: TokenResponse | None = None
    pending: bool = False
    error: str = ""


class OAuthClient:
    """HTTP for the Yandex OAuth device/implicit flow and the api360 org lookup."""

    OAUTH_BASE_URL = "https://oauth.yandex.ru"
    API360_BASE_URL = "https://api360.yandex.net"

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str | None = None,
        timeout_seconds: float,
        retries: int,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._session = requests.Session()
        self._session.hooks["response"].append(log_response)
        adapter = _TimeoutAdapter(max_retries=retry_policy(retries), timeout=timeout_seconds)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def authorize_url(self) -> str:
        """Browser URL for the implicit flow — the user logs in, approves, copies the token."""
        return f"{self.OAUTH_BASE_URL}/authorize?response_type=token&client_id={self._client_id}"

    def request_device_code(self, *, device_name: str | None = None) -> DeviceCodeResponse:
        """``POST /device/code`` — start the device flow. No ``scope`` (uses the app's own)."""
        data = {"client_id": self._client_id}
        if device_name:
            data["device_name"] = device_name
        response = self._session.post(f"{self.OAUTH_BASE_URL}/device/code", data=data)
        _raise_for_error(response)
        return DeviceCodeResponse.model_validate(response.json())

    def poll_token(self, device_code: str) -> TokenPollResult:
        """``POST /token`` once — success, ``authorization_pending``, or a terminal error.

        Only the OAuth error answers (a 400/401 carrying an ``error`` code) are polling states;
        any other failure raises its typed ``YandexError``.
        """
        data = {
            "grant_type": "device_code",
            "code": device_code,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        response = self._session.post(f"{self.OAUTH_BASE_URL}/token", data=data)
        error = _oauth_error(response)
        if not error:
            _raise_for_error(response)
            return TokenPollResult(token=TokenResponse.model_validate(response.json()))
        if error == "authorization_pending":
            return TokenPollResult(pending=True)
        return TokenPollResult(error=error)

    def fetch_organizations(self, token: str) -> list[Organization]:
        """``GET /directory/v1/org`` — the token's orgs, or ``[]`` if it lacks directory scope.

        A 401/403 means the token cannot read the directory; any other failure raises.
        """
        response = self._session.get(
            f"{self.API360_BASE_URL}/directory/v1/org",
            headers={"Authorization": Transport._authorization(token)},
        )
        try:
            _raise_for_error(response)
        except YandexAuthError:
            return []
        return OrganizationList.model_validate(response.json()).organizations
