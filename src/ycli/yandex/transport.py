"""Single auth boundary for every Yandex consumer.

``Transport.session(*, oauth_token, organization_id, timeout_seconds, retries, base)`` returns
a pure ``requests.Session`` carrying ``Authorization: OAuth`` and a single canonical org header
(``X-Org-Id``), a ``urllib3.Retry`` adapter (idempotent methods only — GET/HEAD/OPTIONS;
backoff on 429/5xx) on http/https, and a configured request timeout; non-idempotent POSTs
are NOT retried here — a caller that needs that mounts its own adapter. Credential
resolution is the composition root's concern — this function never reads the environment;
an empty arg raises rather than firing an unauthenticated call.

Example:
    >>> s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    >>> s.headers["Authorization"]
    'OAuth t'
"""

from __future__ import annotations

import threading
import time
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import jwt
import requests
import yandexcloud
from requests import PreparedRequest, Response
from requests.adapters import DEFAULT_POOLBLOCK, DEFAULT_POOLSIZE, DEFAULT_RETRIES, HTTPAdapter
from requests.auth import AuthBase
from urllib3.util.retry import Retry
from yandex.cloud.iam.v1.iam_token_service_pb2 import CreateIamTokenRequest
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub

from ycli.yandex.errors import (
    YandexAuthError,
    YandexClientError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
)

if TYPE_CHECKING:
    from ycli.yandex.auth import ServiceAccountCredentials


class _TimeoutAdapter(HTTPAdapter):
    """HTTPAdapter that applies a default timeout when the caller passes none.

    requests has no session-level default timeout; this injects one so every
    consumer call is bounded even though uplink doesn't thread a timeout through.
    """

    def __init__(
        self,
        pool_connections: int = DEFAULT_POOLSIZE,
        pool_maxsize: int = DEFAULT_POOLSIZE,
        max_retries: int | Retry = DEFAULT_RETRIES,
        pool_block: bool = DEFAULT_POOLBLOCK,
        timeout: float = 30.0,
    ) -> None:
        self._timeout = timeout
        super().__init__(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
            pool_block=pool_block,
        )

    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: Any = None,
        verify: bool | str = True,
        cert: str | tuple[str, str] | None = None,
        proxies: dict[str, str] | None = None,
    ) -> Response:
        if timeout is None:
            timeout = self._timeout
        return super().send(
            request,
            stream=stream,
            timeout=timeout,
            verify=verify,
            cert=cert,
            proxies=proxies,
        )


class _ServiceAccountTokenProvider:
    """Thread-safe lazy IAM token cache backed by Yandex Cloud SDK."""

    _REFRESH_SKEW = timedelta(minutes=5)
    _FALLBACK_LIFETIME = timedelta(minutes=55)

    def __init__(self, credentials: ServiceAccountCredentials) -> None:
        self._credentials = credentials
        sdk = yandexcloud.SDK(service_account_key=credentials.to_yandexcloud_dict())
        self._iam_service = sdk.client(IamTokenServiceStub)
        self._token: str | None = None
        self._refresh_at = datetime.min.replace(tzinfo=UTC)
        self._lock = threading.Lock()

    def get_token(self) -> str:
        now = datetime.now(UTC)
        if self._token is not None and now < self._refresh_at:
            return self._token
        with self._lock:
            now = datetime.now(UTC)
            if self._token is not None and now < self._refresh_at:
                return self._token
            return self._refresh(now)

    def _refresh(self, now: datetime) -> str:
        issued_at = int(time.time())
        encoded_jwt = jwt.encode(
            {
                "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
                "iss": self._credentials.service_account_id,
                "iat": issued_at,
                "exp": issued_at + 3600,
            },
            self._credentials.private_key,
            algorithm="PS256",
            headers={"kid": self._credentials.key_id},
        )
        response = self._iam_service.Create(CreateIamTokenRequest(jwt=encoded_jwt))
        self._token = response.iam_token
        expires_at = getattr(response, "expires_at", None)
        if expires_at is not None and hasattr(expires_at, "ToDatetime"):
            expiration = expires_at.ToDatetime(tzinfo=UTC)
            self._refresh_at = max(now, expiration - self._REFRESH_SKEW)
        else:
            self._refresh_at = now + self._FALLBACK_LIFETIME
        return self._token


class _ServiceAccountAuth(AuthBase):
    """Apply a current service-account IAM token when requests prepares a call."""

    def __init__(self, credentials: ServiceAccountCredentials) -> None:
        self._provider = _ServiceAccountTokenProvider(credentials)

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Authorization"] = f"Bearer {self._provider.get_token()}"
        return r


class Transport:
    """Builds an authed ``requests.Session`` — the single, env-free auth boundary."""

    @staticmethod
    def _authorization(oauth_token: str | None = None, iam_token: str | None = None) -> str | None:
        """The Authorization header value — the single point an auth scheme would vary."""
        if oauth_token:
            return f"OAuth {oauth_token}"
        if iam_token:
            return f"Bearer {iam_token}"
        return None

    @staticmethod
    def _human_detail(response: Response) -> str:
        """The human-readable line from a Yandex error body, or a raw snippet fallback.

        Yandex APIs return ``{"errorMessages": ["…"], …}``; surfacing that message rather
        than the raw JSON keeps CLI errors readable. Parsing the error body is the
        transport's job (ARCH-9) — no downstream surface does it.
        """
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict):
            messages = body.get("errorMessages")
            if isinstance(messages, list) and messages:
                return "; ".join(str(item) for item in messages)
        return response.text[:300].replace("\n", " ").strip()

    @staticmethod
    def _raise_typed(response: Response, *args: Any, **kwargs: Any) -> Response:
        """requests ``response`` hook: turn a final non-2xx into a typed ``YandexError``.

        Runs after urllib3 retries (Retry has ``raise_on_status=False``), so only the
        final response reaches here. uplink calls ``session.request``, which dispatches
        this hook, so every SDK call is covered.
        """
        code = response.status_code
        if code < 400:
            return response
        method = response.request.method
        detail = Transport._human_detail(response)
        message = f"{code} {response.reason} for {method} {response.url}: {detail}"
        url = response.url
        match code:
            case 401 | 403:
                raise YandexAuthError(message, status=code, url=url)
            case 404:
                raise YandexNotFoundError(message, status=code, url=url)
            case 429:
                raise YandexRateLimitError(message, status=code, url=url)
            case _ if code >= 500:
                raise YandexServerError(message, status=code, url=url)
            case _:
                raise YandexClientError(message, status=code, url=url)

    @classmethod
    def session(
        cls,
        *,
        oauth_token: str | None = None,
        iam_token: str | None = None,
        service_account: ServiceAccountCredentials | None = None,
        organization_id: str | None = None,
        cloud_organization_id: str | None = None,
        timeout_seconds: float = 30.0,
        retries: int = 3,
        base: requests.Session | None = None,
    ) -> requests.Session:
        authorization = cls._authorization(oauth_token, iam_token)
        if authorization is None and service_account is None:
            raise ValueError("an OAuth token, IAM token, or service account must be provided")
        if bool(organization_id) == bool(cloud_organization_id):
            raise ValueError("exactly one of organization_id or cloud_organization_id is required")
        if (
            authorization is not None
            and authorization.startswith("Bearer ")
            and not cloud_organization_id
        ):
            raise ValueError("IAM authentication requires cloud_organization_id")
        if authorization is None and not cloud_organization_id:
            raise ValueError("service-account IAM requires cloud_organization_id")
        session = base or requests.Session()
        for header in ("Authorization", "X-Org-Id", "X-Cloud-Org-Id"):
            session.headers.pop(header, None)
        session.auth = None
        if authorization is not None:
            session.headers["Authorization"] = authorization
        else:
            assert service_account is not None
            session.auth = _ServiceAccountAuth(service_account)
        if organization_id:
            session.headers["X-Org-Id"] = organization_id
        else:
            assert cloud_organization_id is not None
            session.headers["X-Cloud-Org-Id"] = cloud_organization_id
        session.hooks["response"].append(cls._raise_typed)
        retry = Retry(
            total=retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
            raise_on_status=False,
        )
        adapter = _TimeoutAdapter(max_retries=retry, timeout=timeout_seconds)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
