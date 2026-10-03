"""How a listing pages: one interface, one class per kind of pagination Yandex APIs use.

A :class:`Pagination` is stateless and does no I/O: :meth:`~Pagination.first` shapes the first
request and :meth:`~Pagination.next` derives the next request from the previous request, its
response and the items it returned, or ``None`` at the end. The same instance therefore serves
sync and async sessions and concurrent walks; the session drives the loop and caps it.

The interface follows dlt's REST client paginators (``dlt.sources.helpers.rest_client``,
Apache-2.0), rewritten for ``httpx2`` requests instead of mutated ``requests`` objects.

Examples:
    >>> import httpx2
    >>> first = OffsetLimitPagination(page_size=2).first(httpx2.Request("GET", "https://x/s"))
    >>> str(first.url)
    'https://x/s?offset=0&limit=2'
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx2

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence


def _with_url(request: httpx2.Request, url: httpx2.URL) -> httpx2.Request:
    """The same request (method, headers, body, extensions) aimed at ``url``.

    ``Host`` is left for httpx2 to derive from ``url``: a next-page link may point elsewhere.
    """
    headers = {name: value for name, value in request.headers.items() if name.lower() != "host"}
    return httpx2.Request(
        request.method,
        url,
        headers=headers,
        content=request.content,
        extensions=request.extensions,
    )


def _with_params(request: httpx2.Request, params: Mapping[str, Any]) -> httpx2.Request:
    return _with_url(request, request.url.copy_merge_params(params))


class Pagination(ABC):
    """One kind of pagination: shape the first request, derive each next one."""

    def first(self, request: httpx2.Request) -> httpx2.Request:
        """The first page's request (by default the endpoint's own request)."""
        return request

    @abstractmethod
    def next(
        self, request: httpx2.Request, response: httpx2.Response, items: Sequence[object]
    ) -> httpx2.Request | None:
        """The next page's request, or ``None`` when ``response`` was the last page."""


@dataclass(frozen=True)
class OffsetLimitPagination(Pagination):
    """``?offset=&limit=`` (Forms surveys): a page shorter than ``page_size`` is the last."""

    page_size: int
    offset_param: str = "offset"
    limit_param: str = "limit"

    def first(self, request: httpx2.Request) -> httpx2.Request:
        """The first page: ``offset`` 0 and ``limit`` of ``page_size``."""
        return _with_params(request, {self.offset_param: 0, self.limit_param: self.page_size})

    def next(
        self, request: httpx2.Request, response: httpx2.Response, items: Sequence[object]
    ) -> httpx2.Request | None:
        """The next offset, or ``None`` after a page shorter than ``page_size``."""
        if len(items) < self.page_size:
            return None
        offset = int(request.url.params[self.offset_param]) + self.page_size
        return _with_params(request, {self.offset_param: offset})


@dataclass(frozen=True)
class PageNumberPagination(Pagination):
    """``?page=&perPage=`` (Tracker): walks to ``X-Total-Pages``, or to a short page without it.

    The header wins when present: a server that caps ``perPage`` below ``page_size`` returns
    short pages that are not the last one.
    """

    page_size: int
    page_param: str = "page"
    size_param: str = "perPage"
    total_pages_header: str | None = "X-Total-Pages"

    def first(self, request: httpx2.Request) -> httpx2.Request:
        """The first page: page 1 of ``page_size`` items."""
        return _with_params(request, {self.page_param: 1, self.size_param: self.page_size})

    def next(
        self, request: httpx2.Request, response: httpx2.Response, items: Sequence[object]
    ) -> httpx2.Request | None:
        """The next page number, or ``None`` after the last page."""
        page = int(request.url.params[self.page_param])
        total = response.headers.get(self.total_pages_header) if self.total_pages_header else None
        last = page >= int(total) if total is not None else len(items) < self.page_size
        return None if last else _with_params(request, {self.page_param: page + 1})


@dataclass(frozen=True)
class CursorPagination(Pagination):
    """A cursor read from the response, sent back as ``?cursor=`` (Wiki ``next_cursor``)."""

    cursor_of: Callable[[httpx2.Response], str | None]
    cursor_param: str = "cursor"

    def next(
        self, request: httpx2.Request, response: httpx2.Response, items: Sequence[object]
    ) -> httpx2.Request | None:
        """The request with the response's cursor, or ``None`` when absent or not advancing."""
        cursor = self.cursor_of(response)
        # A cursor equal to the one just sent means the API stopped advancing.
        if not cursor or request.url.params.get(self.cursor_param) == cursor:
            return None
        return _with_params(request, {self.cursor_param: cursor})


def _scroll_id(response: httpx2.Response) -> str | None:
    return response.headers.get("X-Scroll-Id")


@dataclass(frozen=True)
class HeaderCursorPagination(CursorPagination):
    """A cursor sent in a response header (Tracker scroll: ``X-Scroll-Id`` → ``?scrollId=``)."""

    cursor_of: Callable[[httpx2.Response], str | None] = _scroll_id
    cursor_param: str = "scrollId"


@dataclass(frozen=True)
class LinkHeaderPagination(Pagination):
    """RFC 8288 ``Link: <…>; rel="next"`` (Tracker relative pagination).

    Only the link's query parameters are carried over onto the current request: Tracker prints
    links without a scheme (``<api.tracker.yandex.net/v3/…>``), which would resolve to a wrong
    path if followed as a URL.
    """

    rel: str = "next"

    def next(
        self, request: httpx2.Request, response: httpx2.Response, items: Sequence[object]
    ) -> httpx2.Request | None:
        """The request carrying the ``rel`` link's query, or ``None`` without such a link."""
        link = response.links.get(self.rel)
        if not link:
            return None
        query = httpx2.URL(link["url"]).params
        return _with_url(request, request.url.copy_with(params=query))


@dataclass(frozen=True)
class NextURLPagination(Pagination):
    """A next-page URL in the body (Forms answers ``next.next_url``).

    ``query_only`` carries just the link's query over onto the current request, for an API
    whose links point at a path that does not answer: Forms prints answers links under a
    retired ``/v3/`` route. The request's own parameters (its filters) stay, and the link's
    override them.
    """

    url_of: Callable[[httpx2.Response], str | None]
    query_only: bool = False

    def next(
        self, request: httpx2.Request, response: httpx2.Response, items: Sequence[object]
    ) -> httpx2.Request | None:
        """The request for the body's next-page URL, or ``None`` without one or a repeated one."""
        link = self.url_of(response)
        if not link:
            return None
        url = request.url.join(link)
        if self.query_only:
            url = request.url.copy_merge_params(url.params)
        return None if url == request.url else _with_url(request, url)


@dataclass(frozen=True)
class RelativeIdPagination(Pagination):
    """``?id=<last item's id>`` (Tracker ``_relative`` listings, worklog)."""

    id_of: Callable[[Any], str | None]
    id_param: str = "id"

    def next(
        self, request: httpx2.Request, response: httpx2.Response, items: Sequence[object]
    ) -> httpx2.Request | None:
        """The request after the last item's id, or ``None`` when there is no new id."""
        last = self.id_of(items[-1]) if items else None
        if last is None or request.url.params.get(self.id_param) == last:
            return None
        return _with_params(request, {self.id_param: last})
