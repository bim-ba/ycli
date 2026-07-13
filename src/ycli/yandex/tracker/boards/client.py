"""Declarative Tracker boards client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.boards.models import Board, BoardCreate, BoardList, BoardUpdate


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
        boards = self._drain_relative(
            extract=lambda page: page.root,
            id_of=lambda board: str(board.id) if board.id is not None else None,
            fetch_page=lambda cursor, per_page: self._paginate_page(
                per_page=per_page, board_id=cursor
            ),
            limit=limit,
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

    @uplink.returns.json()
    @uplink.json
    @uplink.post("liveBoards/")
    def _create(self, body: uplink.Body) -> Board:  # ty: ignore[empty-body]
        """``POST /liveBoards/`` — create a board from a ready JSON body (see ``create``)."""

    def create(self, body: BoardCreate) -> Board:
        """Create an agile board from a typed ``BoardCreate`` body. Returns the new ``Board``.

        The endpoint path is literally ``/liveBoards/`` — the older ``POST /boards/`` is
        deprecated and silently ignores the request body.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.boards.create(
            ...     BoardCreate(name="Testing", owner="username")
            ... ).id  # doctest: +SKIP
            1
        """
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("boards/{board_id}")
    def _edit(self, board_id: uplink.Path, body: uplink.Body) -> Board:  # ty: ignore[empty-body]
        """``PATCH /boards/{board_id}`` — edit a board from a ready JSON body (see ``edit``)."""

    def edit(self, board_id: int, body: BoardUpdate) -> Board:
        """Edit an agile board from a typed ``BoardUpdate`` body. Returns the updated ``Board``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.boards.edit(1, BoardUpdate(name="New name")).name  # doctest: +SKIP
            'New name'
        """
        return self._edit(board_id=board_id, body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.delete("boards/{board_id}")
    def delete(self, board_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /boards/{board_id}`` — delete a board (``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.boards.delete(board_id=1).status_code  # doctest: +SKIP
            204
        """
