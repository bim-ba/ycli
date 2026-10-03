"""OAuth device/implicit login HTTP — the ONLY place this feature does HTTP (ARCH-2).

Deliberately does NOT use a core session: the device poll legitimately returns HTTP 400
``authorization_pending`` until the user approves, and a core session raises on every 4xx. So
this builds a plain ``httpx2.Client`` and maps every other failure through
``errors.error_for_status`` itself. Credentials (the user's own client id/secret) arrive as
constructor arguments — this never reads the environment (ARCH-7).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx2

from ycli.log import HTTP_LOGGER_NAME
from ycli.yandex.core import session as core_session
from ycli.yandex.errors import (
    YandexConnectionError,
    describe_error_body,
    error_for_status,
)
from ycli.yandex.status.oauth_models import (
    DeviceCodeResponse,
    TokenResponse,
)

logger = logging.getLogger(HTTP_LOGGER_NAME)

# RFC 6749 §5.2: the token endpoint answers an OAuth error with 400, or 401 for invalid_client.
_OAUTH_ERROR_STATUSES = frozenset({400, 401})


def _log(response: httpx2.Response) -> None:
    logger.info("%s %s -> %s", response.request.method, response.request.url, response.status_code)


def _raise_for_error(response: httpx2.Response) -> None:
    """Raise the typed ``YandexError`` for a non-2xx ``response``, worded like the transport's.

    A 2xx returns ``None``; a 503 HTML page raises ``YandexServerError("503 Service
    Unavailable for POST https://oauth.yandex.ru/device/code: <html>…")``.
    """
    code = response.status_code
    if code < 400:
        return
    detail = describe_error_body(response.text)
    request = response.request
    message = f"{code} {response.reason_phrase} for {request.method} {request.url}: {detail}"
    raise error_for_status(code, message, url=str(request.url))


def _oauth_error(response: httpx2.Response) -> str:
    """The OAuth ``error`` code of a token-endpoint answer, or ``""`` if it carries none.

    A 400 ``{"error": "authorization_pending"}`` gives ``"authorization_pending"``; a 200, a
    503 or a 400 HTML page gives ``""``.
    """
    if response.status_code not in _OAUTH_ERROR_STATUSES:
        return ""
    try:
        body = response.json()
    except ValueError:
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
    """HTTP for the Yandex OAuth device/implicit flow."""

    OAUTH_BASE_URL = "https://oauth.yandex.ru"

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
        # Retries cover a connection that never opened; a request that reached the server is
        # not re-sent, since the device-flow POSTs are not idempotent.
        self._http = httpx2.Client(
            timeout=timeout_seconds,
            event_hooks={"response": [_log]},
            transport=core_session.default_transport() or httpx2.HTTPTransport(retries=retries),
        )

    def _send(
        self,
        method: str,
        url: str,
        *,
        data: dict[str, str | None] | None = None,
    ) -> httpx2.Response:
        # A form field set to None is left out, as the OAuth server expects (no empty secret).
        form = {name: value for name, value in (data or {}).items() if value is not None}
        try:
            return self._http.request(method, url, data=form or None)
        except httpx2.RequestError as exc:
            message = f"{method} {url}: {type(exc).__name__}: {exc}"
            raise YandexConnectionError(message, url=url) from exc

    def authorize_url(self) -> str:
        """Browser URL for the implicit flow — the user logs in, approves, copies the token."""
        return f"{self.OAUTH_BASE_URL}/authorize?response_type=token&client_id={self._client_id}"

    def request_device_code(self, *, device_name: str | None = None) -> DeviceCodeResponse:
        """``POST /device/code`` — start the device flow. No ``scope`` (uses the app's own)."""
        data = {"client_id": self._client_id, "device_name": device_name or None}
        response = self._send("POST", f"{self.OAUTH_BASE_URL}/device/code", data=data)
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
        response = self._send("POST", f"{self.OAUTH_BASE_URL}/token", data=data)
        error = _oauth_error(response)
        if not error:
            _raise_for_error(response)
            return TokenPollResult(token=TokenResponse.model_validate(response.json()))
        if error == "authorization_pending":
            return TokenPollResult(pending=True)
        return TokenPollResult(error=error)
