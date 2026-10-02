"""Every Yandex auth kind as a native ``httpx2.Auth`` — pass one to the session, nothing else.

| Class | Sends | Used by |
|---|---|---|
| :class:`OAuthTokenAuth` | ``OAuth <token>`` | Yandex ID tokens: Tracker, Wiki, Forms, 360 |
| :class:`BotTokenAuth` | ``OAuth <bot token>`` | Yandex Messenger Bot API |
| :class:`IAMTokenAuth` | ``Bearer <IAM token>`` | Yandex Cloud and Cloud-bound services |
| :class:`ServiceAccountAuth` | ``Bearer <IAM token>`` | the same, minted from a key, refreshed |
| :class:`APIKeyAuth` | ``Api-Key <key>`` or a query param | Cloud API keys, Maps ``apikey`` |

All but the query-parameter key go into the ``Authorization`` header.

Secrets are ``SecretStr``, so they never show up in ``repr`` or logs. The organization header
is not auth: it comes from the :class:`~ycli.yandex.core.profile.ServiceProfile`.

Examples:
    >>> import httpx2
    >>> from pydantic import SecretStr
    >>> request = httpx2.Request("GET", "https://api.tracker.yandex.net/v3/myself")
    >>> next(OAuthTokenAuth(SecretStr("y0_token")).auth_flow(request)).headers["Authorization"]
    'OAuth y0_token'
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
import weakref
from datetime import datetime  # pydantic reads the field type at runtime
from pathlib import Path
from typing import TYPE_CHECKING

import httpx2
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from ycli.yandex.errors import describe_error_body, error_for_status

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

IAM_TOKEN_URL = "https://iam.api.cloud.yandex.net/iam/v1/tokens"


class _HeaderAuth(httpx2.Auth):
    """Sets ``Authorization: <scheme> <secret>`` — no I/O, so one flow serves both clients."""

    scheme: str

    def __init__(self, secret: SecretStr) -> None:
        self._secret = secret

    def auth_flow(self, request: httpx2.Request) -> Generator[httpx2.Request, httpx2.Response]:
        request.headers["Authorization"] = f"{self.scheme} {self._secret.get_secret_value()}"
        yield request


class OAuthTokenAuth(_HeaderAuth):
    """A Yandex ID OAuth token (``ycli auth login`` obtains one)."""

    scheme = "OAuth"


class BotTokenAuth(OAuthTokenAuth):
    """A Yandex Messenger bot token, issued in the organization's admin console."""


class IAMTokenAuth(_HeaderAuth):
    """A ready IAM token (``yc iam create-token``); it expires within 12 hours."""

    scheme = "Bearer"


class APIKeyAuth(httpx2.Auth):
    """A static API key: ``Authorization: Api-Key <key>``, or ``?<query_param>=<key>`` (Maps)."""

    def __init__(self, key: SecretStr, *, query_param: str | None = None) -> None:
        self._key = key
        self._query_param = query_param

    def auth_flow(self, request: httpx2.Request) -> Generator[httpx2.Request, httpx2.Response]:
        """Add the key to ``request`` as a header, or as the query parameter if one is set."""
        key = self._key.get_secret_value()
        if self._query_param is None:
            request.headers["Authorization"] = f"Api-Key {key}"
        else:
            request.url = request.url.copy_merge_params({self._query_param: key})
        yield request


class _IAMToken(BaseModel):
    """``POST /iam/v1/tokens`` answer: the token and when it expires."""

    model_config = ConfigDict(populate_by_name=True)

    token: SecretStr = Field(alias="iamToken")
    expires_at: datetime = Field(alias="expiresAt")


class ServiceAccountAuth(httpx2.Auth):
    """A service account's authorized key, exchanged for IAM tokens and refreshed before expiry.

    The key signs a short-lived JWT (PS256); ``POST`` of that JWT to the IAM endpoint returns
    the token. The exchange runs through the same client as the API call (``httpx2`` auth flow),
    so retries, proxies and test transports apply to it too. One token is shared by every call
    until five minutes before it expires; a ``401`` forces one refresh. Needs the
    ``service-account`` extra (PyJWT with ``cryptography``).

    Args:
        service_account_id: The service account's id.
        key_id: The authorized key's id.
        private_key: The key's PEM private key.
        token_url: The IAM endpoint the signed JWT is exchanged at.

    Examples:
        >>> auth = ServiceAccountAuth.from_key_file("authorized_key.json")  # doctest: +SKIP
    """

    requires_response_body = True
    refresh_margin_seconds = 300.0
    jwt_lifetime_seconds = 3600

    def __init__(
        self,
        *,
        service_account_id: str,
        key_id: str,
        private_key: SecretStr,
        token_url: str = IAM_TOKEN_URL,
    ) -> None:
        self._service_account_id = service_account_id
        self._key_id = key_id
        self._private_key = private_key
        self._token_url = token_url
        self._token: SecretStr | None = None
        self._refresh_at = 0.0
        self._lock = threading.Lock()
        self._async_locks: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock] = (
            weakref.WeakKeyDictionary()
        )

    @classmethod
    def from_key_file(cls, path: str | Path) -> ServiceAccountAuth:
        """Load the JSON key ``yc iam key create --output key.json`` writes."""
        key = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            service_account_id=key["service_account_id"],
            key_id=key["id"],
            private_key=SecretStr(key["private_key"]),
        )

    def _token_request(self) -> httpx2.Request:
        try:
            import jwt
        except ModuleNotFoundError as exc:  # pragma: no cover - only without the extra
            raise ModuleNotFoundError(
                "ServiceAccountAuth needs the 'service-account' extra: "
                "uv add 'yandex-cli[service-account]'"
            ) from exc
        now = int(time.time())
        # yc prefixes the PEM with a "PLEASE DO NOT REMOVE THIS LINE!" comment line.
        pem = self._private_key.get_secret_value()
        pem = pem[pem.index("-----BEGIN") :]
        assertion = jwt.encode(
            {
                "iss": self._service_account_id,
                "aud": self._token_url,
                "iat": now,
                "exp": now + self.jwt_lifetime_seconds,
            },
            pem,
            algorithm="PS256",
            headers={"kid": self._key_id},
        )
        return httpx2.Request("POST", self._token_url, json={"jwt": assertion})

    def _store(self, response: httpx2.Response) -> None:
        if response.is_error:
            message = f"IAM token exchange failed: {describe_error_body(response.text)}"
            raise error_for_status(response.status_code, message, url=str(response.url))
        token = _IAMToken.model_validate_json(response.content)
        self._token = token.token
        self._refresh_at = token.expires_at.timestamp() - self.refresh_margin_seconds

    def _needs_token(self) -> bool:
        return self._token is None or time.time() >= self._refresh_at

    def _authorize(self, request: httpx2.Request) -> None:
        assert self._token is not None  # set by _store before any API request
        request.headers["Authorization"] = f"Bearer {self._token.get_secret_value()}"

    def sync_auth_flow(self, request: httpx2.Request) -> Generator[httpx2.Request, httpx2.Response]:
        """Send ``request`` with the shared IAM token, refreshed once after a ``401``."""
        with self._lock:
            if self._needs_token():
                self._store((yield self._token_request()))
        sent_with = self._token
        self._authorize(request)
        response = yield request
        if response.status_code == httpx2.codes.UNAUTHORIZED:
            with self._lock:
                # Refresh once for the whole client: skip it if another call already did.
                if self._token is sent_with:
                    self._store((yield self._token_request()))
            self._authorize(request)
            yield request

    async def async_auth_flow(
        self, request: httpx2.Request
    ) -> AsyncGenerator[httpx2.Request, httpx2.Response]:
        """Send ``request`` with the shared IAM token, refreshed once after a ``401``."""
        lock = self._async_lock()
        async with lock:
            if self._needs_token():
                self._store((yield self._token_request()))
        sent_with = self._token
        self._authorize(request)
        response = yield request
        if response.status_code == httpx2.codes.UNAUTHORIZED:
            async with lock:
                if self._token is sent_with:
                    self._store((yield self._token_request()))
            self._authorize(request)
            yield request

    def _async_lock(self) -> asyncio.Lock:
        """One ``asyncio.Lock`` per event loop: a lock is bound to the loop that first awaits it."""
        loop = asyncio.get_running_loop()
        if loop not in self._async_locks:
            self._async_locks[loop] = asyncio.Lock()
        return self._async_locks[loop]
