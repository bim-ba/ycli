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
- call an optional ``before_send`` hook once per endpoint, with its effect and the built request,
  before the first HTTP attempt (not per retry or page) — the seam a surface uses to confirm or
  refuse a write; the hook decides by returning or by raising, and a request it returns is
  sent in place of the built one; the core knows nothing else;
- walk a paginated listing up to ``limit`` items, warn when items are left behind, and stop on an
  empty page or after ``max_pages`` so a misbehaving cursor cannot loop forever.

Examples:
    >>> from http import HTTPMethod
    >>> from pydantic import SecretStr
    >>> from ycli.yandex.core.auth import OAuthTokenAuth
    >>> from ycli.yandex.core.endpoint import Endpoint
    >>> from ycli.yandex.tracker.client import TrackerClient
    >>> from ycli.yandex.tracker.me.models import Me
    >>> session = connect(
    ...     TrackerClient.profile, auth=OAuthTokenAuth(SecretStr("token")), organization_id="1"
    ... )
    >>> session.send(Endpoint(HTTPMethod.GET, "myself", Me)).login
    'alice'
    >>> session.close()
"""

from __future__ import annotations

import logging
import math
import time
from typing import TYPE_CHECKING

import httpx2
import stamina

from ycli.log import HTTP_LOGGER_NAME
from ycli.settings import HTTPConfig
from ycli.yandex.core.endpoint import PAGED_EXTENSION, check_path
from ycli.yandex.core.listing import AsyncListing, Listing, Walk
from ycli.yandex.errors import (
    YandexConnectionError,
    YandexError,
    YandexRateLimitError,
    YandexServerError,
    YandexStaleContinuationError,
    describe_error_body,
    error_for_status,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable, Iterator

    from ycli.yandex.core.endpoint import Effect, Endpoint, Paged
    from ycli.yandex.core.profile import ServiceProfile

# Called once per endpoint with what it does to the server and the request about to be sent.
type BeforeSend = Callable[[Effect, httpx2.Request], httpx2.Request | None]

logger = logging.getLogger(HTTP_LOGGER_NAME)

# Query parameters that carry a secret (API keys sent as ``?apikey=``) are masked in logs/errors.
_SECRET_PARAMS = frozenset({"apikey", "api_key", "access_token", "oauth_token", "token"})


def shown(url: httpx2.URL) -> httpx2.URL:
    """``url`` with secret query parameters masked, safe to log or put in an error message."""
    secrets = [name for name in url.params if name.lower() in _SECRET_PARAMS]
    return url.copy_merge_params(dict.fromkeys(secrets, "***")) if secrets else url


def _announce(
    before_send: BeforeSend | None, endpoint: Endpoint, request: httpx2.Request
) -> httpx2.Request:
    """Tell the ``before_send`` hook, if there is one, what ``endpoint`` is about to do.

    Args:
        before_send: The hook, or ``None``.
        endpoint: The endpoint being sent.
        request: The request built for it.

    Returns:
        The request to send: the hook's own when it hands one back, else ``request``.
    """
    if before_send is None:
        return request
    return before_send(endpoint.effect, request) or request


def _retry_after(response: httpx2.Response) -> float | None:
    """``Retry-After`` in seconds; ``None`` for an HTTP-date or a value that is not a delay."""
    try:
        seconds = float(response.headers.get("Retry-After", "nan"))
    except ValueError:
        return None
    return seconds if math.isfinite(seconds) and seconds >= 0 else None


def _checked(response: httpx2.Response, elapsed_seconds: float) -> httpx2.Response:
    """Log the exchange; raise the typed error for a non-2xx response."""
    request = response.request
    logger.info(
        "%s %s -> %s (%.0f ms)",
        request.method,
        shown(request.url),
        response.status_code,
        elapsed_seconds * 1000,
    )
    # ``next_request`` is set only on a located redirect an endpoint asked not to follow; any other
    # 3xx (a 304, a redirect without a Location) is an error like a 4xx.
    if response.is_success or response.next_request is not None:
        return response
    detail = describe_error_body(response.text)
    message = (
        f"{response.status_code} {response.reason_phrase} for {request.method} "
        f"{shown(request.url)}: {detail}"
    )
    raise error_for_status(
        response.status_code,
        message,
        url=str(shown(request.url)),
        retry_after=_retry_after(response),
    )


def _retry_policy(
    *, idempotent: bool, max_retry_after_seconds: float
) -> Callable[[Exception], bool | float]:
    """Stamina's ``on`` hook: whether (and after how many seconds) to retry ``exception``."""

    def decide(exception: Exception) -> bool | float:
        if isinstance(exception, YandexRateLimitError):
            if exception.retry_after is None:
                return True  # no hint: stamina's exponential backoff
            if exception.retry_after > max_retry_after_seconds:
                return False  # fail now rather than hang for minutes
            return exception.retry_after
        return idempotent and isinstance(exception, YandexServerError | YandexConnectionError)

    return decide


def _log_retry(request: httpx2.Request, attempt: int, attempts: int) -> None:
    if attempt > 1:
        logger.info(
            "retrying %s %s (attempt %d of %d)",
            request.method,
            shown(request.url),
            attempt,
            attempts,
        )


def _stale(walk: Walk, paged: Paged, error: YandexError) -> YandexError:
    """``error`` as what it means for the first request of a continued listing.

    A status the way of paging answers a dead continuation with is told as that: the caller
    starts again. Anything else stays what it is.
    """
    if not walk.resuming or error.status not in paged.pagination.stale_statuses:
        return error
    return YandexStaleContinuationError(
        f"the listing cannot go on from this token any more; start it again without it ({error})",
        status=error.status,
        url=error.url,
    )


def _ended(walk: Walk, limit: int | None, pages: int, max_pages: int) -> None:
    """Say in the log why a walk ended short of the listing's end."""
    if walk.truncated:
        logger.warning(
            "stopped at %d items; more may be available (raise the limit, or use --all in the CLI)",
            limit,
        )
    elif walk.request is not None and pages >= max_pages:
        logger.warning("stopped after %d pages; the listing did not end", max_pages)


def _first_page(paged: Paged, client: httpx2.Client | httpx2.AsyncClient) -> httpx2.Request:
    """The request for a listing's first page; it and the pages after it carry ``paged``."""
    request = paged.pagination.first(paged.endpoint.request(client))
    request.extensions[PAGED_EXTENSION] = paged
    return request


class SyncSession:
    """Sends endpoints through an ``httpx2.Client`` — the blocking flavour."""

    def __init__(
        self,
        client: httpx2.Client,
        *,
        http: HTTPConfig | None = None,
        before_send: BeforeSend | None = None,
    ) -> None:
        self._client = client
        self._http = http or HTTPConfig()
        self._attempts = self._http.retries + 1
        self._before_send = before_send

    def _send(
        self, request: httpx2.Request, *, idempotent: bool, follow_redirects: bool = True
    ) -> httpx2.Response:
        check_path(request.url.raw_path.decode().partition("?")[0])
        retrying = stamina.retry_context(
            on=_retry_policy(
                idempotent=idempotent,
                max_retry_after_seconds=self._http.max_retry_after_seconds,
            ),
            attempts=self._attempts,
            timeout=None,
        )
        for attempt in retrying:
            with attempt:
                _log_retry(request, attempt.num, self._attempts)
                started = time.perf_counter()
                try:
                    response = self._client.send(request, follow_redirects=follow_redirects)
                except httpx2.RequestError as exc:
                    url = shown(request.url)
                    message = f"{request.method} {url}: {type(exc).__name__}: {exc}"
                    raise YandexConnectionError(message, url=str(url)) from exc
                return _checked(response, time.perf_counter() - started)
        raise AssertionError("stamina returns or raises inside the loop")  # pragma: no cover

    def send[T](self, endpoint: Endpoint[T]) -> T:
        """Call ``endpoint`` once and return its parsed response."""
        request = endpoint.request(self._client)
        request = _announce(self._before_send, endpoint, request)
        response = self._send(
            request,
            idempotent=endpoint.idempotent,
            follow_redirects=endpoint.follow_redirects,
        )
        return endpoint.parse(response)

    def iterate[P, I](
        self,
        paged: Paged[P, I],
        *,
        limit: int | None = None,
        next: str | None = None,  # noqa: A002 - the caller's word, on every surface (#502)
    ) -> Listing[I]:
        """The listing's items, fetched page by page as they are asked for.

        Args:
            paged: The listing.
            limit: The most items to give; ``None`` gives all.
            next: What an earlier call of the same listing returned, to go on from there.

        Returns:
            The items, lazily; when they end, whether there is more and how to go on.
        """
        # The hook hears of a listing once, as before: its first request stands for all pages.
        first = _announce(self._before_send, paged.endpoint, _first_page(paged, self._client))
        longest = self._http.max_token_length
        walk = Walk(paged, first, limit=limit, token=next, longest_token=longest)

        def pages() -> Iterator[I]:
            asked = 0
            while walk.request is not None and asked < self._http.max_pages:
                try:
                    response = self._send(
                        walk.request,
                        idempotent=paged.endpoint.idempotent,
                        follow_redirects=paged.endpoint.follow_redirects,
                    )
                except YandexError as error:
                    raise _stale(walk, paged, error) from error
                asked += 1
                yield from walk.take(response)
            _ended(walk, limit, asked, self._http.max_pages)

        return Listing(walk, pages)

    def close(self) -> None:
        """Close the underlying ``httpx2.Client``."""
        self._client.close()


class AsyncSession:
    """Sends endpoints through an ``httpx2.AsyncClient`` — the same contract, awaited."""

    def __init__(
        self,
        client: httpx2.AsyncClient,
        *,
        http: HTTPConfig | None = None,
        before_send: BeforeSend | None = None,
    ) -> None:
        self._client = client
        self._http = http or HTTPConfig()
        self._attempts = self._http.retries + 1
        self._before_send = before_send

    async def _send(
        self, request: httpx2.Request, *, idempotent: bool, follow_redirects: bool = True
    ) -> httpx2.Response:
        check_path(request.url.raw_path.decode().partition("?")[0])
        retrying = stamina.retry_context(
            on=_retry_policy(
                idempotent=idempotent,
                max_retry_after_seconds=self._http.max_retry_after_seconds,
            ),
            attempts=self._attempts,
            timeout=None,
        )
        async for attempt in retrying:
            with attempt:
                _log_retry(request, attempt.num, self._attempts)
                started = time.perf_counter()
                try:
                    response = await self._client.send(request, follow_redirects=follow_redirects)
                except httpx2.RequestError as exc:
                    url = shown(request.url)
                    message = f"{request.method} {url}: {type(exc).__name__}: {exc}"
                    raise YandexConnectionError(message, url=str(url)) from exc
                return _checked(response, time.perf_counter() - started)
        raise AssertionError("stamina returns or raises inside the loop")  # pragma: no cover

    async def send[T](self, endpoint: Endpoint[T]) -> T:
        """Call ``endpoint`` once and return its parsed response."""
        request = endpoint.request(self._client)
        request = _announce(self._before_send, endpoint, request)
        response = await self._send(
            request,
            idempotent=endpoint.idempotent,
            follow_redirects=endpoint.follow_redirects,
        )
        return endpoint.parse(response)

    def iterate[P, I](
        self,
        paged: Paged[P, I],
        *,
        limit: int | None = None,
        next: str | None = None,  # noqa: A002 - the caller's word, on every surface (#502)
    ) -> AsyncListing[I]:
        """The listing's items, fetched page by page as they are asked for.

        Args:
            paged: The listing.
            limit: The most items to give; ``None`` gives all.
            next: What an earlier call of the same listing returned, to go on from there.

        Returns:
            The items, lazily; when they end, whether there is more and how to go on.
        """
        # The hook hears of a listing once, as before: its first request stands for all pages.
        first = _announce(self._before_send, paged.endpoint, _first_page(paged, self._client))
        longest = self._http.max_token_length
        walk = Walk(paged, first, limit=limit, token=next, longest_token=longest)

        async def pages() -> AsyncIterator[I]:
            asked = 0
            while walk.request is not None and asked < self._http.max_pages:
                try:
                    response = await self._send(
                        walk.request,
                        idempotent=paged.endpoint.idempotent,
                        follow_redirects=paged.endpoint.follow_redirects,
                    )
                except YandexError as error:
                    raise _stale(walk, paged, error) from error
                asked += 1
                for item in walk.take(response):
                    yield item
            _ended(walk, limit, asked, self._http.max_pages)

        return AsyncListing(walk, pages)

    async def aclose(self) -> None:
        """Close the underlying ``httpx2.AsyncClient``."""
        await self._client.aclose()


def default_transport() -> httpx2.MockTransport | None:
    """The network when the caller passes none: ``None`` means httpx2's own.

    The one seam tests replace to answer core requests with an ``httpx2.MockTransport``, which
    serves both the sync and the async client.
    """
    return None


def connect(
    profile: ServiceProfile,
    *,
    auth: httpx2.Auth,
    organization_id: str | None = None,
    cloud_organization_id: str | None = None,
    http: HTTPConfig | None = None,
    transport: httpx2.BaseTransport | None = None,
    before_send: BeforeSend | None = None,
) -> SyncSession:
    """A :class:`SyncSession` for one service: base URL, org header, auth, timeout, retries.

    ``transport`` replaces the network (``httpx2.MockTransport`` in tests); ``before_send`` is
    called once per endpoint, before its first attempt (see the module docstring).
    """
    http = http or HTTPConfig()
    client = httpx2.Client(
        base_url=profile.base_url.rstrip("/") + "/",
        headers=profile.headers_for(organization_id, cloud_organization_id),
        auth=auth,
        timeout=http.timeout_seconds,
        # Tracker answers an old key of a moved issue with a redirect to the new one.
        follow_redirects=True,
        transport=transport if transport is not None else default_transport(),
    )
    return SyncSession(client, http=http, before_send=before_send)


def connect_async(
    profile: ServiceProfile,
    *,
    auth: httpx2.Auth,
    organization_id: str | None = None,
    cloud_organization_id: str | None = None,
    http: HTTPConfig | None = None,
    transport: httpx2.AsyncBaseTransport | None = None,
    before_send: BeforeSend | None = None,
) -> AsyncSession:
    """The :class:`AsyncSession` twin of :func:`connect`."""
    http = http or HTTPConfig()
    client = httpx2.AsyncClient(
        base_url=profile.base_url.rstrip("/") + "/",
        headers=profile.headers_for(organization_id, cloud_organization_id),
        auth=auth,
        timeout=http.timeout_seconds,
        # Tracker answers an old key of a moved issue with a redirect to the new one.
        follow_redirects=True,
        transport=transport if transport is not None else default_transport(),
    )
    return AsyncSession(client, http=http, before_send=before_send)
