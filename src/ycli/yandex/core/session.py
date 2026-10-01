"""Thin sessions that send :class:`~ycli.yandex.core.endpoint.Endpoint` objects over ``httpx2``.

Everything that does not touch the network — building the request, parsing the response,
deciding the next page — lives in the endpoint and the pagination, so :class:`SyncSession`
and :class:`AsyncSession` differ only in ``await``. Both:

- raise a typed :class:`~ycli.yandex.errors.YandexError` for any non-2xx answer and
  :class:`~ycli.yandex.errors.YandexConnectionError` when no answer arrives;
- retry with backoff (``stamina``): a ``429`` always, honouring ``Retry-After``; a ``5xx`` or a
  lost connection only for idempotent endpoints, never for a create;
- log one line per request (method, URL, status, duration) and one per retry to ``ycli.http``,
  never headers or bodies;
- walk a paginated listing up to ``limit`` items, warn when items are left behind, and stop on an
  empty page or after ``max_pages`` so a misbehaving cursor cannot loop forever.

Example:
    >>> session = connect(
    ...     TRACKER, auth=OAuthTokenAuth(token), organization_id="1"
    ... )  # doctest: +SKIP
    >>> session.send(Endpoint("GET", "myself", Me)).login  # doctest: +SKIP
    'alice'
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import httpx2
import stamina

from ycli.settings import HTTPConfig
from ycli.yandex.errors import (
    YandexConnectionError,
    YandexRateLimitError,
    YandexServerError,
    describe_error_body,
    error_for_status,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable, Iterator, Sequence

    from ycli.yandex.core.endpoint import Endpoint, Paged
    from ycli.yandex.core.profile import ServiceProfile

logger = logging.getLogger("ycli.http")

DEFAULT_MAX_PAGES = 1000


def _retry_after(response: httpx2.Response) -> float | None:
    value = response.headers.get("Retry-After")
    try:
        return float(value) if value is not None else None
    except ValueError:  # an HTTP-date; let the backoff decide instead
        return None


def _checked(response: httpx2.Response, elapsed_seconds: float) -> httpx2.Response:
    """Log the exchange; raise the typed error for a non-2xx response."""
    request = response.request
    logger.info(
        "%s %s -> %s (%.0f ms)",
        request.method,
        request.url,
        response.status_code,
        elapsed_seconds * 1000,
    )
    if response.is_success:
        return response
    detail = describe_error_body(response.text)
    message = (
        f"{response.status_code} {response.reason_phrase} for {request.method} {request.url}: "
        f"{detail}"
    )
    raise error_for_status(
        response.status_code, message, url=str(request.url), retry_after=_retry_after(response)
    )


def _retry_policy(idempotent: bool) -> Callable[[Exception], bool | float]:
    """stamina's ``on`` hook: whether (and after how many seconds) to retry ``exception``."""

    def decide(exception: Exception) -> bool | float:
        if isinstance(exception, YandexRateLimitError):
            return exception.retry_after if exception.retry_after is not None else True
        return idempotent and isinstance(exception, YandexServerError | YandexConnectionError)

    return decide


def _log_retry(request: httpx2.Request, attempt: int, attempts: int) -> None:
    if attempt > 1:
        logger.info(
            "retrying %s %s (attempt %d of %d)", request.method, request.url, attempt, attempts
        )


def _page_plan[I](
    items: Sequence[I], produced: int, limit: int | None, has_next: bool
) -> tuple[Sequence[I], bool]:
    """Which of a page's ``items`` to yield, and whether the walk ends after them.

    Warns when the cap leaves items behind — on this page or on pages not yet fetched.
    """
    if limit is None:
        return items, not has_next
    room = limit - produced
    if len(items) > room or (len(items) == room and has_next):
        logger.warning(
            "stopped at %d items; more are available (raise the limit, or use --all in the CLI)",
            limit,
        )
        return items[:room], True
    return items, not has_next or len(items) == room


class SyncSession:
    """Sends endpoints through an ``httpx2.Client`` — the blocking flavour."""

    def __init__(self, client: httpx2.Client, *, retries: int = HTTPConfig().retries) -> None:
        self._client = client
        self._attempts = retries + 1

    def _send(self, request: httpx2.Request, idempotent: bool) -> httpx2.Response:
        retrying = stamina.retry_context(
            on=_retry_policy(idempotent), attempts=self._attempts, timeout=None
        )
        for attempt in retrying:
            with attempt:
                _log_retry(request, attempt.num, self._attempts)
                started = time.perf_counter()
                try:
                    response = self._client.send(request)
                except httpx2.TransportError as exc:
                    message = f"{request.method} {request.url}: {exc!r}"
                    raise YandexConnectionError(message, url=str(request.url)) from exc
                return _checked(response, time.perf_counter() - started)
        raise AssertionError("stamina returns or raises inside the loop")  # pragma: no cover

    def send[T](self, endpoint: Endpoint[T]) -> T:
        """Call ``endpoint`` once and return its parsed response."""
        response = self._send(endpoint.request(self._client), endpoint.idempotent)
        return endpoint.parse(response)

    def iterate[P, I](
        self, paged: Paged[P, I], *, limit: int | None = None, max_pages: int = DEFAULT_MAX_PAGES
    ) -> Iterator[I]:
        """Yield the listing's items page by page, at most ``limit`` (``None`` = all)."""
        request = paged.pagination.first(paged.endpoint.request(self._client))
        produced = 0
        for _ in range(max_pages):
            response = self._send(request, paged.endpoint.idempotent)
            items: Sequence[I] = paged.items_of(paged.endpoint.parse(response))
            following = paged.pagination.next(request, response, items) if items else None
            taken, done = _page_plan(items, produced, limit, following is not None)
            produced += len(taken)
            yield from taken
            if done or following is None:
                return
            request = following
        logger.warning("stopped after %d pages; the listing did not end", max_pages)

    def close(self) -> None:
        self._client.close()


class AsyncSession:
    """Sends endpoints through an ``httpx2.AsyncClient`` — the same contract, awaited."""

    def __init__(self, client: httpx2.AsyncClient, *, retries: int = HTTPConfig().retries) -> None:
        self._client = client
        self._attempts = retries + 1

    async def _send(self, request: httpx2.Request, idempotent: bool) -> httpx2.Response:
        retrying = stamina.retry_context(
            on=_retry_policy(idempotent), attempts=self._attempts, timeout=None
        )
        async for attempt in retrying:
            with attempt:
                _log_retry(request, attempt.num, self._attempts)
                started = time.perf_counter()
                try:
                    response = await self._client.send(request)
                except httpx2.TransportError as exc:
                    message = f"{request.method} {request.url}: {exc!r}"
                    raise YandexConnectionError(message, url=str(request.url)) from exc
                return _checked(response, time.perf_counter() - started)
        raise AssertionError("stamina returns or raises inside the loop")  # pragma: no cover

    async def send[T](self, endpoint: Endpoint[T]) -> T:
        """Call ``endpoint`` once and return its parsed response."""
        response = await self._send(endpoint.request(self._client), endpoint.idempotent)
        return endpoint.parse(response)

    async def iterate[P, I](
        self, paged: Paged[P, I], *, limit: int | None = None, max_pages: int = DEFAULT_MAX_PAGES
    ) -> AsyncIterator[I]:
        """Yield the listing's items page by page, at most ``limit`` (``None`` = all)."""
        request = paged.pagination.first(paged.endpoint.request(self._client))
        produced = 0
        for _ in range(max_pages):
            response = await self._send(request, paged.endpoint.idempotent)
            items: Sequence[I] = paged.items_of(paged.endpoint.parse(response))
            following = paged.pagination.next(request, response, items) if items else None
            taken, done = _page_plan(items, produced, limit, following is not None)
            produced += len(taken)
            for item in taken:
                yield item
            if done or following is None:
                return
            request = following
        logger.warning("stopped after %d pages; the listing did not end", max_pages)

    async def aclose(self) -> None:
        await self._client.aclose()


def default_transport() -> httpx2.BaseTransport | None:
    """The network for :func:`connect` when the caller passes none (``None`` = httpx2's own).

    The one seam tests replace to answer core requests with an ``httpx2.MockTransport``.
    """
    return None


def connect(
    profile: ServiceProfile,
    *,
    auth: httpx2.Auth,
    organization_id: str | None = None,
    http: HTTPConfig | None = None,
    transport: httpx2.BaseTransport | None = None,
) -> SyncSession:
    """A :class:`SyncSession` for one service: base URL, org header, auth, timeout, retries.

    ``transport`` replaces the network (``httpx2.MockTransport`` in tests).
    """
    http = http or HTTPConfig()
    client = httpx2.Client(
        base_url=profile.base_url.rstrip("/") + "/",
        headers=profile.headers_for(organization_id),
        auth=auth,
        timeout=http.timeout_seconds,
        transport=transport if transport is not None else default_transport(),
    )
    return SyncSession(client, retries=http.retries)


def connect_async(
    profile: ServiceProfile,
    *,
    auth: httpx2.Auth,
    organization_id: str | None = None,
    http: HTTPConfig | None = None,
    transport: httpx2.AsyncBaseTransport | None = None,
) -> AsyncSession:
    """The :class:`AsyncSession` twin of :func:`connect`."""
    http = http or HTTPConfig()
    client = httpx2.AsyncClient(
        base_url=profile.base_url.rstrip("/") + "/",
        headers=profile.headers_for(organization_id),
        auth=auth,
        timeout=http.timeout_seconds,
        transport=transport,
    )
    return AsyncSession(client, retries=http.retries)
