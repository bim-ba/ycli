"""Wiki ``/grids`` client on the httpx2 core — dynamic tables."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import Ack
from ycli.yandex.wiki.grids import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.grids.models import (
        CellsUpdateResult,
        ColumnSuggestion,
        ColumnUpdateResult,
        Grid,
        GridCloneOperation,
        RevisionResult,
        RowsAddResult,
        RowUpdateResult,
    )


class GridsClient(Resource):
    """``/grids`` — dynamic tables (CRUD + rows/columns/cells + clone).

    Reads: :meth:`get`, :meth:`suggest_column`. Writes: :meth:`create`, :meth:`update`,
    :meth:`delete`, the row/column add/remove/move calls, :meth:`update_cells`, the async
    :meth:`clone`, :meth:`update_column` and :meth:`update_row`.
    Every mutating body carries a ``revision`` for optimistic locking except ``create`` (no prior
    revision) and ``clone`` (a deferred trigger); ``update_column`` and ``update_row`` take one but
    the API does not enforce it there.

    ``suggest_column``, ``update_column`` and ``update_row`` call operations Yandex does not
    document (they are in the live OpenAPI only), so their contract may change without notice.
    """

    def get(
        self,
        grid_id: str,
        fields: str | None = None,
        row_filter: str | None = None,
        only_cols: str | None = None,
        only_rows: str | None = None,
        revision: str | None = None,
        sort: str | None = None,
    ) -> Grid:
        """``GET /grids/{id}`` → the full :class:`~ycli.yandex.wiki.grids.models.Grid`.

        ``fields`` adds optional blocks (``attributes``, ``user_permissions``); ``row_filter`` /
        ``only_cols`` / ``only_rows`` / ``sort`` narrow the returned rows and columns server-side;
        ``revision`` loads a historical version. Read the ``revision`` off the result to drive any
        subsequent write's optimistic lock.

        Args:
            grid_id: The grid's id.
            fields: The optional blocks to add: ``attributes``, ``user_permissions``.
            row_filter: The server-side row filter.
            only_cols: The columns to return.
            only_rows: The rows to return.
            revision: The historical revision to load.
            sort: The sort order of the rows.

        Returns:
            The grid.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> wiki.grids.get(grid_id).revision
            '12'
        """
        return self._session.send(
            endpoints.get_grid(
                grid_id,
                fields=fields,
                row_filter=row_filter,
                only_cols=only_cols,
                only_rows=only_rows,
                revision=revision,
                sort=sort,
            )
        )

    def create(self, body: dict[str, Any]) -> Grid:
        """``POST /grids`` — create a grid as a page resource. ``body`` is a dumped ``GridCreate``.

        Args:
            body: The new grid: its title and the page it goes on.

        Returns:
            The created grid.

        Examples:
            >>> body = {"title": "Hiring plan", "page": {"slug": "hr/hiring"}}
            >>> wiki.grids.create(body).title
            'Hiring plan'
        """
        return self._session.send(endpoints.create_grid(body))

    def update(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``POST /grids/{id}`` — rename / re-sort (POST not PATCH). ``body`` carries ``revision``.

        ``body`` is a dumped ``GridUpdate``; its ``default_sort`` must use the *write* shape
        ``[{"<column_slug>": "asc"|"desc"}]`` — the ``{slug, title, direction}`` read shape
        returned by :meth:`get` is rejected with a 400.

        Args:
            grid_id: The grid's id.
            body: The changes, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> body = {
            ...     "revision": "12",
            ...     "title": "Roadmap 2027",
            ...     "default_sort": [{"due": "desc"}],
            ... }
            >>> wiki.grids.update(grid_id, body).revision
            '13'
        """
        return self._session.send(endpoints.update_grid(grid_id, body))

    def delete(self, grid_id: str) -> Ack:
        """``DELETE /grids/{id}`` → an :class:`Ack` (``204 No Content``).

        The API returns no body, so the result is synthesized; a non-2xx status raises a typed
        ``YandexError`` before this returns.

        Args:
            grid_id: The grid's id.

        Returns:
            The acknowledgement of the delete.

        Examples:
            >>> wiki.grids.delete("0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a03").ok
            True
        """
        self._session.send(endpoints.delete_grid(grid_id))
        return Ack.deleted("grid", grid_id)

    def add_rows(self, grid_id: str, body: dict[str, Any]) -> RowsAddResult:
        """``POST /grids/{id}/rows`` — insert rows. ``body`` is a dumped ``RowsAdd`` (+ revision).

        Args:
            grid_id: The grid's id.
            body: The rows to add, with the grid's ``revision``.

        Returns:
            The grid's new revision and the added rows.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> rows = [{"name": "Launch", "owner": "vera"}]
            >>> wiki.grids.add_rows(grid_id, {"revision": "13", "rows": rows}).revision
            '14'
        """
        return self._session.send(endpoints.add_rows(grid_id, body))

    def remove_rows(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``DELETE /grids/{id}/rows`` — delete rows by id. ``body`` is a dumped ``RowsRemove``.

        A rare DELETE-with-body: ``row_ids`` + ``revision`` travel in the JSON body.

        Args:
            grid_id: The grid's id.
            body: The ids of the rows to delete, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> wiki.grids.remove_rows(
            ...     grid_id, {"revision": "14", "row_ids": ["r1", "r2"]}
            ... ).revision
            '15'
        """
        return self._session.send(endpoints.remove_rows(grid_id, body))

    def move_rows(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``POST /grids/{id}/rows/move`` — reorder rows. ``body`` is a dumped ``RowsMove``.

        Args:
            grid_id: The grid's id.
            body: The row to move and where, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> wiki.grids.move_rows(
            ...     grid_id, {"revision": "15", "row_id": "r3", "position": 4}
            ... ).revision
            '16'
        """
        return self._session.send(endpoints.move_rows(grid_id, body))

    def add_columns(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``POST /grids/{id}/columns`` — add columns. ``body`` is a dumped ``ColumnsAdd``.

        The API requires a ``slug`` on every column (400 ``value_error.missing`` without one);
        ``ColumnsAdd`` derives it from the title when omitted, but a raw dict body passed here
        directly must carry it.

        Args:
            grid_id: The grid's id.
            body: The columns to add, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> columns = [{"title": "Due Date", "type": "date", "slug": "due_date"}]
            >>> wiki.grids.add_columns(grid_id, {"revision": "16", "columns": columns}).revision
            '17'
        """
        return self._session.send(endpoints.add_columns(grid_id, body))

    def remove_columns(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``DELETE /grids/{id}/columns`` — delete columns by slug. ``body`` is a ``ColumnsRemove``.

        A rare DELETE-with-body: ``column_slugs`` + ``revision`` travel in the JSON body.

        Args:
            grid_id: The grid's id.
            body: The slugs of the columns to delete, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> body = {"revision": "17", "column_slugs": ["stage", "due_date"]}
            >>> wiki.grids.remove_columns(grid_id, body).revision
            '18'
        """
        return self._session.send(endpoints.remove_columns(grid_id, body))

    def move_columns(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``POST /grids/{id}/columns/move`` — reorder columns. ``body`` is a ``ColumnsMove`` dump.

        Args:
            grid_id: The grid's id.
            body: The column to move and where, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> body = {"revision": "18", "column_slug": "owner", "position": 0}
            >>> wiki.grids.move_columns(grid_id, body).revision
            '19'
        """
        return self._session.send(endpoints.move_columns(grid_id, body))

    def update_cells(self, grid_id: str, body: dict[str, Any]) -> CellsUpdateResult:
        """``POST /grids/{id}/cells`` — set individual cell values. ``body`` is a ``CellsUpdate``.

        Args:
            grid_id: The grid's id.
            body: The cells to set, with the grid's ``revision``.

        Returns:
            The grid's new revision and the updated cells.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> cells = [{"row_id": 101, "column_slug": "name", "value": "Launch v2"}]
            >>> wiki.grids.update_cells(grid_id, {"revision": "19", "cells": cells}).revision
            '20'
        """
        return self._session.send(endpoints.update_cells(grid_id, body))

    def clone(self, grid_id: str, body: dict[str, Any]) -> GridCloneOperation:
        """``POST /grids/{id}/clone`` — copy the grid onto another page (async trigger).

        Returns a :class:`~ycli.yandex.wiki.grids.models.GridCloneOperation`; poll its
        ``operation.id`` via ``OperationsClient.gridclone_get`` until terminal. ``body`` is a
        dumped ``GridClone`` (``{target, title?, with_data}``).

        Args:
            grid_id: The grid's id.
            body: The target page, an optional title and whether to copy the data.

        Returns:
            The clone operation to poll.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> body = {"target": "eng/roadmap-copy", "title": "Roadmap copy", "with_data": True}
            >>> wiki.grids.clone(grid_id, body).operation.id
            'task-6201'
        """
        return self._session.send(endpoints.clone_grid(grid_id, body))

    def suggest_column(self, grid_id: str, body: dict[str, Any]) -> ColumnSuggestion:
        """``POST /grids/{id}/columns/suggest`` — is a column slug free? (undocumented, may change).

        A read despite the POST: it changes nothing. ``body`` is a dumped :class:`ColumnSuggest`
        (``{title?, slug?}``); a ``title`` is turned into a slug first. The reply says whether the
        slug is ``occupied`` and lists free alternatives.

        Args:
            grid_id: The grid's id.
            body: The column's ``title`` and/or ``slug``.

        Returns:
            Whether the slug is occupied, with free alternatives.

        Examples:
            >>> wiki.grids.suggest_column(
            ...     "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a02", {"title": "Due date"}
            ... ).occupied
            False
        """
        return self._session.send(endpoints.suggest_column(grid_id, body))

    def update_column(
        self, grid_id: str, column_slug: str, body: dict[str, Any]
    ) -> ColumnUpdateResult:
        """``POST /grids/{id}/column/{slug}`` — edit a column in place (undocumented, may change).

        The only way to change a column after creating it; its ``type`` and ``slug`` stay. ``body``
        is a dumped :class:`ColumnUpdate`: only the fields sent change. ``revision`` is accepted but
        not enforced (a stale or missing one works) and every call moves the grid's revision on.
        Returns the new revision and the column as saved.

        Args:
            grid_id: The grid's id.
            column_slug: The column's slug.
            body: The fields to change.

        Returns:
            The grid's new revision and the column as saved.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> wiki.grids.update_column(grid_id, "stage", {"title": "Stage 2"}).column.title
            'Stage 2'
        """
        return self._session.send(endpoints.update_column(grid_id, column_slug, body))

    def update_row(self, grid_id: str, row_id: str, body: dict[str, Any]) -> RowUpdateResult:
        """``POST /grids/{id}/rows/{row_id}`` — pin or colour one row (undocumented, may change).

        ``body`` is a dumped :class:`RowUpdate` (``{revision?, pinned?, color?}``). The reply is a
        bare acknowledgement without the new revision (read it with :meth:`get`); ``revision`` is
        accepted but not enforced, and every call moves the grid's revision on.

        Args:
            grid_id: The grid's id.
            row_id: The row's id.
            body: The row's ``pinned`` and ``color``, and optionally ``revision``.

        Returns:
            The acknowledgement of the change.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> wiki.grids.update_row(grid_id, "103", {"pinned": True, "color": "orange"})
            RowUpdateResult(...)
        """
        return self._session.send(endpoints.update_row(grid_id, row_id, body))
