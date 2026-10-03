"""Tracker board ``/columns`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.columns import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.columns.models import Column, ColumnCreate, ColumnUpdate


class ColumnsClient(Resource):
    """List, get, create, edit and delete the columns of an agile board."""

    def list(self, board_id: int) -> ItemList[Column]:
        """``GET /boards/{board_id}/columns`` → the board's column listing.

        Args:
            board_id: The board's id.

        Returns:
            The board's columns.

        Examples:
            >>> tracker.columns.list(73).root[0].name
            'Open'
        """
        return self._session.send(endpoints.list_columns(board_id))

    def get(self, board_id: int, column_id: int) -> Column:
        """``GET /boards/{board_id}/columns/{column_id}`` → a single board column.

        Args:
            board_id: The board's id.
            column_id: The column's id.

        Returns:
            The column.

        Examples:
            >>> tracker.columns.get(74, 2).name
            'Review'
        """
        return self._session.send(endpoints.get_column(board_id, column_id))

    def create(self, board_id: int, body: ColumnCreate) -> Column:
        """Create a board column from a typed ``ColumnCreate`` body. Returns the new ``Column``.

        Args:
            board_id: The board's id.
            body: The new column's settings.

        Returns:
            The created column.

        Examples:
            >>> from ycli.yandex.tracker.columns.models import ColumnCreate
            >>> tracker.columns.create(
            ...     75, ColumnCreate(name="Approve", statuses=["needInfo", "adjustment"])
            ... ).id
            5
        """
        return self._session.send(endpoints.create_column(board_id, body))

    def edit(self, board_id: int, column_id: int, body: ColumnUpdate) -> Column:
        """Edit a board column from a typed ``ColumnUpdate`` body. Returns the updated ``Column``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Args:
            board_id: The board's id.
            column_id: The column's id.
            body: The fields to change.

        Returns:
            The updated column.

        Examples:
            >>> from ycli.yandex.tracker.columns.models import ColumnUpdate
            >>> tracker.columns.edit(76, 6, ColumnUpdate(name="Pause")).name
            'Pause'
        """
        return self._session.send(endpoints.edit_column(board_id, column_id, body))

    def delete(self, board_id: int, column_id: int) -> None:
        """``DELETE /boards/{board_id}/columns/{column_id}`` — delete a column (``204``, no body).

        Args:
            board_id: The board's id.
            column_id: The column's id.

        Examples:
            >>> tracker.columns.delete(78, 8)
        """
        self._session.send(endpoints.delete_column(board_id, column_id))
