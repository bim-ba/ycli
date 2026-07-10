"""Pagination strategies — drain an API's page mechanics into a bounded flat list.

Each strategy owns ONE cursor mechanic and accepts injected page-access callables, so the
public client method never exposes a cursor: it picks a strategy, says how to read a page,
and gets back a list capped at ``limit`` (``None`` = uncapped). Pure — no HTTP here.

Generic over the page type ``P`` (whatever ``fetch_page`` returns — a pydantic model in
production, a plain ``dict`` in tests) and the item type ``T``. The injected callables do
all structural access, so no page Protocol is imposed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class PaginationStrategy[P, T](ABC):
    @abstractmethod
    def collect(self, fetch_page: Callable[..., P], limit: int | None) -> list[T]:
        """Accumulate items by driving ``fetch_page`` until exhausted or ``limit`` reached.

        The abstract cursor type is left open (``Callable[..., P]``): each concrete strategy
        pins it — ``str | None`` for the ``next``/id cursors, ``int`` for :class:`OffsetStrategy`.
        """


class SinglePageStrategy[P, T](PaginationStrategy[P, T]):
    def __init__(self, *, extract: Callable[[P], list[T]]) -> None:
        self._extract = extract

    def collect(self, fetch_page: Callable[[str | None], P], limit: int | None) -> list[T]:
        items = list(self._extract(fetch_page(None)))
        return items if limit is None else items[:limit]

    @classmethod
    def collect_wrapped[R](
        cls,
        page_fn: Callable[[str | None], P],
        *,
        extract: Callable[[P], list[T]],
        wrap: Callable[[list[T]], R],
        limit: int | None = None,
    ) -> R:
        """Single-page envelope -> bounded, wrapped flat collection (the wiki/forms list shape)."""
        return wrap(cls(extract=extract).collect(page_fn, limit))


class CursorStrategy[P, T](PaginationStrategy[P, T]):
    def __init__(
        self, *, extract: Callable[[P], list[T]], next_of: Callable[[P], str | None]
    ) -> None:
        self._extract = extract
        self._next_of = next_of

    def collect(self, fetch_page: Callable[[str | None], P], limit: int | None) -> list[T]:
        items: list[T] = []
        cursor: str | None = None
        while True:
            page = fetch_page(cursor)
            items.extend(self._extract(page))
            if limit is not None and len(items) >= limit:
                return items[:limit]
            cursor = self._next_of(page)
            if cursor is None:
                return items

    @classmethod
    def collect_wrapped[R](
        cls,
        page_fn: Callable[[str | None], P],
        *,
        extract: Callable[[P], list[T]],
        next_of: Callable[[P], str | None],
        wrap: Callable[[list[T]], R],
        limit: int | None = None,
    ) -> R:
        """Cursor envelope -> bounded, wrapped flat collection (the wiki cursor list shape)."""
        return wrap(cls(extract=extract, next_of=next_of).collect(page_fn, limit))


class NextUrlStrategy[P, T](PaginationStrategy[P, T]):
    """HATEOAS: the first page comes from ``fetch_page``; subsequent ones from ``fetch_url``."""

    def __init__(
        self,
        *,
        extract: Callable[[P], list[T]],
        next_url_of: Callable[[P], str | None],
        fetch_url: Callable[[str], P],
    ) -> None:
        self._extract = extract
        self._next_url_of = next_url_of
        self._fetch_url = fetch_url

    def collect(self, fetch_page: Callable[[str | None], P], limit: int | None) -> list[T]:
        page = fetch_page(None)
        items: list[T] = list(self._extract(page))
        seen: set[str] = set()
        url = self._next_url_of(page)
        while url is not None and url not in seen:
            if limit is not None and len(items) >= limit:
                break
            seen.add(url)
            page = self._fetch_url(url)
            items.extend(self._extract(page))
            url = self._next_url_of(page)
        return items if limit is None else items[:limit]


class OffsetStrategy[P, T](PaginationStrategy[P, T]):
    """Offset/limit paging: advance an integer ``offset`` by ``page_size`` until a short page.

    The API returns at most ``page_size`` items per request; ``fetch_page`` receives the next
    ``offset`` (``0, page_size, 2*page_size, …``) and must ask for that page size. A page
    shorter than ``page_size`` — including an empty one — means the listing is exhausted, so
    there is always at most one "extra" request when the total is an exact multiple of
    ``page_size``. Drives Forms ``/surveys`` and Tracker ``perPage``/``page`` listings.

    Note the ``fetch_page`` cursor is an ``int`` offset here, not the ``str | None`` cursor of
    the sibling strategies.
    """

    def __init__(self, *, extract: Callable[[P], list[T]], page_size: int) -> None:
        self._extract = extract
        self._page_size = page_size

    def collect(self, fetch_page: Callable[[int], P], limit: int | None) -> list[T]:
        items: list[T] = []
        offset = 0
        while True:
            page_items = list(self._extract(fetch_page(offset)))
            items.extend(page_items)
            if limit is not None and len(items) >= limit:
                return items[:limit]
            if len(page_items) < self._page_size:
                return items
            offset += self._page_size


class RelativeCursorStrategy[P, T](PaginationStrategy[P, T]):
    """Id-cursor paging: each request repeats with ``id=<last returned item's id>``.

    Like :class:`CursorStrategy`, but the next cursor is derived from the LAST item of the page
    rather than a ``next`` field the envelope hands back (Tracker ``_relative`` / ``worklog``
    ``id=`` scrolling). Terminal when a page comes back empty — there is no last item to
    advance from — or when that last item yields no id. Empty is the shortest possible page,
    so a short/empty final page ends the walk.
    """

    def __init__(
        self, *, extract: Callable[[P], list[T]], id_of: Callable[[T], str | None]
    ) -> None:
        self._extract = extract
        self._id_of = id_of

    def collect(self, fetch_page: Callable[[str | None], P], limit: int | None) -> list[T]:
        items: list[T] = []
        cursor: str | None = None
        while True:
            page_items = list(self._extract(fetch_page(cursor)))
            if not page_items:
                return items
            items.extend(page_items)
            if limit is not None and len(items) >= limit:
                return items[:limit]
            cursor = self._id_of(page_items[-1])
            if cursor is None:
                return items
