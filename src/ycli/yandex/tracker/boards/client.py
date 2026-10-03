"""Tracker ``/boards`` client on the httpx2 core."""

from __future__ import annotations

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.boards import endpoints
from ycli.yandex.tracker.boards.models import Board, BoardCreate, BoardUpdate


class BoardsClient(Resource):
    """List (relative-paginated), get, create, edit and delete agile boards."""

    def list(self, *, limit: int | None = None) -> ItemList[Board]:
        """All agile boards in the organisation, draining the ``id=<last board id>`` cursor.

        ``/boards/_paginate`` sorts by ascending board id; each next page repeats with
        ``id=<id of the last board seen>`` until a page comes back empty. Capped at ``limit``
        (``None`` = every board); a small cap narrows the page to ``limit`` rows.

        Args:
            limit: The most boards to return; ``None`` returns every board.

        Returns:
            The boards, in ascending id order.

        Examples:
            >>> [board.name for board in tracker.boards.list(limit=500).root]
            ['Alpha', 'Beta', 'Gamma']
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_boards(page_size=page_size)
        return ItemList[Board](list(self._session.iterate(paged, limit=limit)))

    def get(self, board_id: int) -> Board:
        """``GET /boards/{board_id}`` → a single agile board.

        Args:
            board_id: The board's id.

        Returns:
            The board.

        Examples:
            >>> tracker.boards.get(31).name
            'Kanban'
        """
        return self._session.send(endpoints.get_board(board_id))

    def create(self, body: BoardCreate) -> Board:
        """Create an agile board from a typed ``BoardCreate`` body. Returns the new ``Board``.

        The endpoint path is literally ``/liveBoards/`` — the older ``POST /boards/`` is
        deprecated and silently ignores the request body.

        Args:
            body: The new board's settings.

        Returns:
            The created board.

        Examples:
            >>> tracker.boards.create(BoardCreate(name="Release train", owner="alice")).id
            41
        """
        return self._session.send(endpoints.create_board(body))

    def edit(self, board_id: int, body: BoardUpdate) -> Board:
        """Edit an agile board from a typed ``BoardUpdate`` body. Returns the updated ``Board``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Args:
            board_id: The board's id.
            body: The fields to change.

        Returns:
            The updated board.

        Examples:
            >>> tracker.boards.edit(51, BoardUpdate(name="Renamed board")).name
            'Renamed board'
        """
        return self._session.send(endpoints.edit_board(board_id, body))

    def delete(self, board_id: int) -> None:
        """``DELETE /boards/{board_id}`` — delete a board (``204``, empty body).

        Args:
            board_id: The board's id.

        Examples:
            >>> tracker.boards.delete(61)
        """
        self._session.send(endpoints.delete_board(board_id))
