"""Tracker ``/boards`` client on the httpx2 core."""

from __future__ import annotations

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.boards import endpoints
from ycli.yandex.tracker.boards.models import Board, BoardCreate, BoardList, BoardUpdate


class BoardsClient(Resource):
    """List (relative-paginated), get, create, edit and delete agile boards."""

    def list(self, *, limit: int | None = None) -> BoardList:
        """All agile boards in the organisation, draining the ``id=<last board id>`` cursor.

        ``/boards/_paginate`` sorts by ascending board id; each next page repeats with
        ``id=<id of the last board seen>`` until a page comes back empty. Capped at ``limit``
        (``None`` = every board); a small cap narrows the page to ``limit`` rows.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.boards.list(limit=50).root[0].name  # doctest: +SKIP
            'My board'
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_boards(page_size=page_size)
        return BoardList(list(self._session.iterate(paged, limit=limit)))

    def get(self, board_id: int) -> Board:
        """``GET /boards/{board_id}`` → a single agile board.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.boards.get(board_id=1).name  # doctest: +SKIP
            'My board'
        """
        return self._session.send(endpoints.get_board(board_id))

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
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_board(dumped))

    def edit(self, board_id: int, body: BoardUpdate) -> Board:
        """Edit an agile board from a typed ``BoardUpdate`` body. Returns the updated ``Board``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.boards.edit(1, BoardUpdate(name="New name")).name  # doctest: +SKIP
            'New name'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_board(board_id, dumped))

    def delete(self, board_id: int) -> None:
        """``DELETE /boards/{board_id}`` — delete a board (``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.boards.delete(board_id=1)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_board(board_id))
