"""Single auth boundary for every Yandex consumer.

``Transport.session(*, token, org_id)`` returns a pure ``requests.Session``
carrying ``Authorization: OAuth`` and a single canonical org header (``X-Org-Id``),
a ``urllib3.Retry`` adapter (idempotent methods only — GET/HEAD/OPTIONS; total=3
with backoff on 429/5xx) on http/https, and a default request timeout;
non-idempotent POSTs are NOT retried here — a caller that needs that mounts its
own adapter. Credential resolution is the consumer's ``from_env`` concern — this
function never reads ``os.environ``; an empty arg raises rather than firing an
unauthenticated call.

Example:
    >>> s = Transport.session(token="t", org_id="o")
    >>> s.headers["Authorization"]
    'OAuth t'
"""

from __future__ import annotations

from typing import Any, ClassVar

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


def _raise_typed(response: Response, *args: Any, **kwargs: Any) -> Response:
    """requests ``response`` hook: turn a final non-2xx into a typed ``YandexError``.

    Runs after urllib3 retries (Retry has ``raise_on_status=False``), so only the
    final response reaches here. uplink calls ``session.request``, which dispatches
    this hook, so every SDK call is covered.
    """
    code = response.status_code
    if code < 400:
        return response
    snippet = response.text[:300].replace("\n", " ").strip()
    msg = f"{code} {response.reason} for {response.request.method} {response.url}: {snippet}"
    url = response.url
    if code in (401, 403):
        raise YandexAuthError(msg, status=code, url=url)
    if code == 404:
        raise YandexNotFoundError(msg, status=code, url=url)
    if code == 429:
        raise YandexRateLimitError(msg, status=code, url=url)
    if code >= 500:
        raise YandexServerError(msg, status=code, url=url)
    raise YandexClientError(msg, status=code, url=url)


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
    """Builds an authed ``requests.Session`` — the single auth boundary.

    PURE: ``session(*, token, org_id)`` never reads ``os.environ`` (credential
    resolution is a consumer's ``from_env`` concern). Config (timeout, retry total,
    org-header name) lives as ClassVars — no module-level globals. The org header is
    a single canonical ``X-Org-Id`` (case-insensitive per RFC 9110 → serves all APIs).
    POSTs are NOT retried (non-idempotent); only GET/HEAD/OPTIONS.

    Example:
        >>> s = Transport.session(token="t", org_id="o")
        >>> s.headers["Authorization"], s.headers["X-Org-Id"]
        ('OAuth t', 'o')
    """

    TIMEOUT_S: ClassVar[float] = 30.0
    RETRY_TOTAL: ClassVar[int] = 3
    ORG_HEADER: ClassVar[str] = "X-Org-Id"

    @classmethod
    def session(cls, *, token: str, org_id: str) -> requests.Session:
        """Return a configured ``requests.Session``. Raises ``ValueError`` on an empty arg.

        Example:
            >>> Transport.session(token="", org_id="o")
            Traceback (most recent call last):
            ValueError: token must be a non-empty string
        """
        if not token:
            raise ValueError("token must be a non-empty string")
        if not org_id:
            raise ValueError("org_id must be a non-empty string")
        session = requests.Session()
        session.headers.update({"Authorization": f"OAuth {token}", cls.ORG_HEADER: org_id})
        session.hooks["response"].append(_raise_typed)
        retry = Retry(
            total=cls.RETRY_TOTAL,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
            raise_on_status=False,
        )
        adapter = _TimeoutAdapter(max_retries=retry, timeout=cls.TIMEOUT_S)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
