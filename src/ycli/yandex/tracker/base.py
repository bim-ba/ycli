"""Per-domain base — carries the Tracker API base_url; resource clients inherit it.

NOTE: no ``from __future__ import annotations`` — resource clients subclass this and
uplink reads their method annotations eagerly. Keep this module annotation-eager too.
"""

from collections.abc import Callable
from typing import ClassVar

from ycli.yandex.base import BaseYandex
from ycli.yandex.pagination import RelativeCursorStrategy


class TrackerResource(BaseYandex):
    """Base for every Tracker resource client (inherits session DI via constructor)."""

    base_url: ClassVar[str] = "https://api.tracker.yandex.net/v3"

    def _drain_relative[P, T](
        self,
        *,
        extract: Callable[[P], list[T]],
        id_of: Callable[[T], str | None],
        fetch_page: Callable[[str | None, int], P],
        limit: int | None,
        max_page_size: int = 100,
    ) -> list[T]:
        """Drain a relative-cursor (``id=<last item's id>``) Tracker listing to a flat list.

        Centralizes the ``RelativeCursorStrategy`` boilerplate shared by every Tracker
        relative-cursor endpoint (history, comments, changelog, users, boards, worklog) plus
        the page-size clamp: a positive ``limit`` narrows the first (and only, since a single
        page then satisfies it) request to ``min(max_page_size, limit)`` rows instead of always
        fetching a full ``max_page_size`` page. ``limit`` of ``None``/``0`` ("fetch everything")
        keeps requesting full ``max_page_size`` pages.
        """
        per_page = min(max_page_size, limit) if limit else max_page_size
        strategy = RelativeCursorStrategy(extract=extract, id_of=id_of)
        return strategy.collect(lambda cursor: fetch_page(cursor, per_page), limit)
