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
    def collect(self, fetch_page: Callable[[str | None], P], limit: int | None) -> list[T]:
        """Accumulate items by driving ``fetch_page`` until exhausted or ``limit`` reached."""


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
