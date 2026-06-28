"""Pagination strategies — drain an API's page mechanics into a bounded flat list.

Each strategy owns ONE cursor mechanic and accepts injected page-access callables, so the
public client method never exposes a cursor: it picks a strategy, says how to read a page,
and gets back a list capped at ``limit`` (``None`` = uncapped). Pure — no HTTP here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class PaginationStrategy(ABC):
    @abstractmethod
    def collect(self, fetch_page: Callable[[Any], Any], limit: int | None) -> list:
        """Accumulate items by driving ``fetch_page`` until exhausted or ``limit`` reached."""


class SinglePageStrategy(PaginationStrategy):
    def __init__(self, *, extract: Callable[[Any], list]) -> None:
        self._extract = extract

    def collect(self, fetch_page: Callable[[Any], Any], limit: int | None) -> list:
        items = list(self._extract(fetch_page(None)))
        return items if limit is None else items[:limit]


class CursorStrategy(PaginationStrategy):
    def __init__(self, *, extract: Callable[[Any], list], next_of: Callable[[Any], Any]) -> None:
        self._extract = extract
        self._next_of = next_of

    def collect(self, fetch_page: Callable[[Any], Any], limit: int | None) -> list:
        items: list = []
        cursor: Any = None
        while True:
            page = fetch_page(cursor)
            items.extend(self._extract(page))
            if limit is not None and len(items) >= limit:
                return items[:limit]
            cursor = self._next_of(page)
            if not cursor:
                return items


class NextUrlStrategy(PaginationStrategy):
    """HATEOAS: the first page comes from ``fetch_page``; subsequent ones from ``fetch_url``."""

    def __init__(
        self,
        *,
        extract: Callable[[Any], list],
        next_url_of: Callable[[Any], Any],
        fetch_url: Callable[[str], Any],
    ) -> None:
        self._extract = extract
        self._next_url_of = next_url_of
        self._fetch_url = fetch_url

    def collect(self, fetch_page: Callable[[Any], Any], limit: int | None) -> list:
        page = fetch_page(None)
        items: list = list(self._extract(page))
        seen: set[str] = set()
        url = self._next_url_of(page)
        while url and url not in seen:
            if limit is not None and len(items) >= limit:
                break
            seen.add(url)
            page = self._fetch_url(url)
            items.extend(self._extract(page))
            url = self._next_url_of(page)
        return items if limit is None else items[:limit]
