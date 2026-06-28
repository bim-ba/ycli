"""Single auth boundary for every Yandex consumer.

``Transport.session(*, token, organization_id, timeout_seconds, retries)`` returns a pure
``requests.Session`` carrying ``Authorization: OAuth`` and a single canonical org header
(``X-Org-Id``), a ``urllib3.Retry`` adapter (idempotent methods only — GET/HEAD/OPTIONS;
backoff on 429/5xx) on http/https, and a configured request timeout; non-idempotent POSTs
are NOT retried here — a caller that needs that mounts its own adapter. Credential
resolution is the consumer's ``from_env`` concern — this function never reads
``os.environ``; an empty arg raises rather than firing an unauthenticated call.

Example:
    >>> s = Transport.session(token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    >>> s.headers["Authorization"]
    'OAuth t'
"""

from __future__ import annotations

from typing import Any

import requests
from requests import PreparedRequest, Response
from requests.adapters import DEFAULT_POOLBLOCK, DEFAULT_POOLSIZE, DEFAULT_RETRIES, HTTPAdapter
from urllib3.util.retry import Retry

from ycli.yandex.errors import (
    YandexAuthError,
    YandexClientError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
)

ORGANIZATION_HEADER = "X-Org-Id"


def _raise_typed(response: Response, *args: Any, **kwargs: Any) -> Response:
    """requests ``response`` hook: turn a final non-2xx into a typed ``YandexError``.

    Runs after urllib3 retries (Retry has ``raise_on_status=False``), so only the
    final response reaches here. uplink calls ``session.request``, which dispatches
    this hook, so every SDK call is covered.
    """
    code = response.status_code
    message = f"{code} {response.reason} for {response.request.method} {response.url}: {response.text[:300].replace(chr(10), ' ').strip()}"
    url = response.url
    match code:
        case _ if code < 400:
            return response
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

    @classmethod
    def session(
        cls,
        *,
        token: str,
        organization_id: str,
        timeout_seconds: float,
        retries: int,
    ) -> requests.Session:
        if not token:
            raise ValueError("token must be a non-empty string")
        if not organization_id:
            raise ValueError("organization_id must be a non-empty string")
        session = requests.Session()
        session.headers.update(
            {"Authorization": f"OAuth {token}", ORGANIZATION_HEADER: organization_id}
        )
        session.hooks["response"].append(_raise_typed)
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
