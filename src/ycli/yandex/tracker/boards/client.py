"""Declarative Tracker boards client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.pagination import RelativeCursorStrategy
from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.boards.models import Board, BoardList


class BoardsClient(TrackerResource):
    """Declarative HTTP for ``/boards`` (relative-paginated list + get by id)."""

    @uplink.returns.json()
    @uplink.get("boards/_paginate")
    def _paginate_page(
        self,
        per_page: uplink.Query("perPage") = 100,  # ty: ignore[invalid-type-form]
        board_id: uplink.Query("id") = None,  # ty: ignore[invalid-type-form]
    ) -> BoardList:  # ty: ignore[empty-body]
        """One raw ``/boards/_paginate`` page (a bare JSON array); callers use ``list``."""

    def list(self, *, limit: int | None = None) -> BoardList:
        """All agile boards in the organisation, draining the ``id=<last board id>`` cursor.

        ``/boards/_paginate`` sorts by ascending board id and returns at most 500 rows per
        page; each next page repeats with ``id=<id of the last board seen>`` until a page comes
        back empty. Capped at ``limit`` (``None`` = every board).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.boards.list(limit=50).root[0].name  # doctest: +SKIP
            'My board'
        """
        strategy = RelativeCursorStrategy(
            extract=lambda page: page.root,
            id_of=lambda board: str(board.id) if board.id is not None else None,
        )
        boards = strategy.collect(
            lambda cursor: self._paginate_page(per_page=100, board_id=cursor),
            limit,
        )
        return BoardList(boards)

    @uplink.returns.json()
    @uplink.get("boards/{board_id}")
    def get(self, board_id: uplink.Path) -> Board:  # ty: ignore[empty-body]
        """``GET /boards/{board_id}`` → a single agile board.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.boards.get(board_id=1).name  # doctest: +SKIP
            'My board'
        """
