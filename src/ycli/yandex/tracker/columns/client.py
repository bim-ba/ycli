"""Declarative Tracker board columns client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.columns.models import Column, ColumnCreate, ColumnList, ColumnUpdate


class ColumnsClient(TrackerResource):
    """Declarative HTTP for board ``/columns`` (list + get + create/edit/delete)."""

    @uplink.returns.json()
    @uplink.get("boards/{board_id}/columns")
    def list(self, board_id: uplink.Path) -> ColumnList:  # ty: ignore[empty-body]
        """``GET /boards/{board_id}/columns`` → the board's column listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.list(board_id=73).root[0].name  # doctest: +SKIP
            'Open'
        """

    @uplink.returns.json()
    @uplink.get("boards/{board_id}/columns/{column_id}")
    def get(self, board_id: uplink.Path, column_id: uplink.Path) -> Column:  # ty: ignore[empty-body]
        """``GET /boards/{board_id}/columns/{column_id}`` → a single board column.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.get(board_id=73, column_id=1).name  # doctest: +SKIP
            'Open'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("boards/{board_id}/columns/")
    def _create(self, board_id: uplink.Path, body: uplink.Body) -> Column:  # ty: ignore[empty-body]
        """``POST /boards/{board_id}/columns/`` — create from a ready JSON body (see ``create``)."""

    def create(self, board_id: int, body: ColumnCreate) -> Column:
        """Create a board column from a typed ``ColumnCreate`` body. Returns the new ``Column``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.create(
            ...     73, ColumnCreate(name="Approve", statuses=["needInfo"])
            ... ).id  # doctest: +SKIP
            5
        """
        return self._create(
            board_id=board_id, body=body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("boards/{board_id}/columns/{column_id}")
    def _edit(self, board_id: uplink.Path, column_id: uplink.Path, body: uplink.Body) -> Column:  # ty: ignore[empty-body]
        """``PATCH /boards/{board_id}/columns/{column_id}`` — edit from a body (see ``edit``)."""

    def edit(self, board_id: int, column_id: int, body: ColumnUpdate) -> Column:
        """Edit a board column from a typed ``ColumnUpdate`` body. Returns the updated ``Column``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.edit(73, 5, ColumnUpdate(name="Pause")).name  # doctest: +SKIP
            'Pause'
        """
        return self._edit(
            board_id=board_id,
            column_id=column_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
        )

    @uplink.delete("boards/{board_id}/columns/{column_id}")
    def delete(self, board_id: uplink.Path, column_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /boards/{board_id}/columns/{column_id}`` — delete a column (``204``, no body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.columns.delete(board_id=73, column_id=5).status_code  # doctest: +SKIP
            204
        """
