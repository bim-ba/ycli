"""Single auth boundary for every Yandex consumer.

``Transport.session(*, oauth_token, organization_id, timeout_seconds, retries, base)`` returns
a pure ``requests.Session`` carrying ``Authorization: OAuth`` and the single canonical org
header (``ORG_HEADER``), a ``urllib3.Retry`` adapter (idempotent methods only —
GET/HEAD/OPTIONS; backoff on 429/5xx) on http/https, and a configured request timeout;
non-idempotent POSTs are NOT retried here — a caller that needs that mounts its own adapter.
Credential resolution is the composition root's concern — this function never reads the environment;
an empty arg raises rather than firing an unauthenticated call.

Example:
    >>> s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    >>> s.headers["Authorization"]
    'OAuth t'
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Self

import requests
from requests import PreparedRequest, Response
from requests.adapters import DEFAULT_POOLBLOCK, DEFAULT_POOLSIZE, DEFAULT_RETRIES, HTTPAdapter
from urllib3.util.retry import Retry

if TYPE_CHECKING:
    from types import TracebackType

    from urllib3 import BaseHTTPResponse
    from urllib3.connectionpool import ConnectionPool

from ycli.yandex.core.profile import ORG_HEADER
from ycli.yandex.errors import describe_error_body, error_for_status

logger = logging.getLogger("ycli.http")


class _LoggedRetry(Retry):
    """``urllib3.Retry`` that logs each retry it decides to make (urllib3 itself stays quiet)."""

    def increment(
        self,
        method: str | None = None,
        url: str | None = None,
        response: BaseHTTPResponse | None = None,
        error: Exception | None = None,
        _pool: ConnectionPool | None = None,
        _stacktrace: TracebackType | None = None,
    ) -> Self:
        retry = super().increment(method, url, response, error, _pool, _stacktrace)
        cause = response.status if response is not None else error
        logger.info("retrying %s %s after %s (%s left)", method, url, cause, retry.total)
        return retry


def retry_policy(retries: int) -> Retry:
    """Back off and retry idempotent requests (GET/HEAD/OPTIONS) on 429 and 5xx, up to ``retries``.

    Example:
        >>> retry_policy(3).total
        3
    """
    return _LoggedRetry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
        raise_on_status=False,
    )


def log_response(response: Response, *args: Any, **kwargs: Any) -> Response:
    """requests ``response`` hook: one INFO line per final response — never headers or bodies."""
    request = response.request
    logger.info(
        "%s %s -> %s (%.0f ms)",
        request.method,
        request.url,
        response.status_code,
        response.elapsed.total_seconds() * 1000,
    )
    return response


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


class Transport:
    """Builds an authed ``requests.Session`` — the single, env-free auth boundary."""

    @staticmethod
    def _authorization(oauth_token: str) -> str:
        """The Authorization header value — the single point an auth scheme would vary."""
        return f"OAuth {oauth_token}"

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
        detail = describe_error_body(response.text)
        message = f"{code} {response.reason} for {response.request.method} {response.url}: {detail}"
        raise error_for_status(code, message, url=response.url)

    @classmethod
    def session(
        cls,
        *,
        oauth_token: str,
        organization_id: str,
        timeout_seconds: float = 30.0,
        retries: int = 3,
        base: requests.Session | None = None,
    ) -> requests.Session:
        if not oauth_token:
            raise ValueError("oauth_token must be a non-empty string")
        if not organization_id:
            raise ValueError("organization_id must be a non-empty string")
        session = base or requests.Session()
        session.headers.update(
            {"Authorization": cls._authorization(oauth_token), ORG_HEADER: organization_id}
        )
        session.hooks["response"].extend([log_response, cls._raise_typed])
        adapter = _TimeoutAdapter(max_retries=retry_policy(retries), timeout=timeout_seconds)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
