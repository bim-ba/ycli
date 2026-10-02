"""Tracker board ``/columns`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.columns import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.columns.models import Column, ColumnCreate, ColumnList, ColumnUpdate


class ColumnsClient(Resource):
    """List, get, create, edit and delete the columns of an agile board."""

    def list(self, board_id: int) -> ColumnList:
        """``GET /boards/{board_id}/columns`` → the board's column listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.list(board_id=73).root[0].name  # doctest: +SKIP
            'Open'
        """
        return self._session.send(endpoints.list_columns(board_id))

    def get(self, board_id: int, column_id: int) -> Column:
        """``GET /boards/{board_id}/columns/{column_id}`` → a single board column.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.get(board_id=73, column_id=1).name  # doctest: +SKIP
            'Open'
        """
        return self._session.send(endpoints.get_column(board_id, column_id))

    def create(self, board_id: int, body: ColumnCreate) -> Column:
        """Create a board column from a typed ``ColumnCreate`` body. Returns the new ``Column``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.create(
            ...     73, ColumnCreate(name="Approve", statuses=["needInfo"])
            ... ).id  # doctest: +SKIP
            5
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_column(board_id, dumped))

    def edit(self, board_id: int, column_id: int, body: ColumnUpdate) -> Column:
        """Edit a board column from a typed ``ColumnUpdate`` body. Returns the updated ``Column``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.edit(73, 5, ColumnUpdate(name="Pause")).name  # doctest: +SKIP
            'Pause'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_column(board_id, column_id, dumped))

    def delete(self, board_id: int, column_id: int) -> None:
        """``DELETE /boards/{board_id}/columns/{column_id}`` — delete a column (``204``, no body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.delete(board_id=73, column_id=5)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_column(board_id, column_id))
