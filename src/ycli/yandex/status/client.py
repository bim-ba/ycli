"""OAuth device/implicit login HTTP — the ONLY place this feature does HTTP (ARCH-2).

Deliberately does NOT use ``Transport.session``: the device poll legitimately returns
HTTP 400 ``authorization_pending`` until the user approves, and Transport installs a
raise-on-4xx hook that would turn that expected 400 into an exception. So this builds a
plain ``requests.Session`` and inspects status codes itself, reusing transport's
``_TimeoutAdapter`` for a bounded timeout and its ``Authorization: OAuth`` scheme for the
api360 org lookup. Credentials (the user's own client id/secret) arrive as constructor
arguments — this never reads the environment (ARCH-7).
"""

from __future__ import annotations

from dataclasses import dataclass

import requests
from urllib3.util.retry import Retry

from ycli.yandex.status.oauth_models import (
    DeviceCodeResponse,
    Organization,
    OrganizationList,
    TokenResponse,
)
from ycli.yandex.transport import Transport, _TimeoutAdapter

_HTTP_OK = 200


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
        timeout_seconds: int = 30,
        retries: int = 3,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
            raise_on_status=False,
        )
        adapter = _TimeoutAdapter(max_retries=retry, timeout=timeout_seconds)
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
        return DeviceCodeResponse.model_validate(response.json())

    def poll_token(self, device_code: str) -> TokenPollResult:
        """``POST /token`` once — success, ``authorization_pending``, or a terminal error."""
        data = {
            "grant_type": "device_code",
            "code": device_code,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        response = self._session.post(f"{self.OAUTH_BASE_URL}/token", data=data)
        if response.status_code == _HTTP_OK:
            return TokenPollResult(token=TokenResponse.model_validate(response.json()))
        error = response.json().get("error", "")
        if error == "authorization_pending":
            return TokenPollResult(pending=True)
        return TokenPollResult(error=error or "authorization failed")

    def fetch_organizations(self, token: str) -> list[Organization]:
        """``GET /directory/v1/org`` — the token's orgs, or ``[]`` if it lacks directory scope."""
        authorization = Transport._authorization(token)
        assert authorization is not None
        response = self._session.get(
            f"{self.API360_BASE_URL}/directory/v1/org",
            headers={"Authorization": authorization},
        )
        if response.status_code != _HTTP_OK:
            return []
        return OrganizationList.model_validate(response.json()).organizations
