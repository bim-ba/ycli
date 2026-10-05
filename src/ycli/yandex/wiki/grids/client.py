"""Wiki ``/grids`` client on the httpx2 core — dynamic tables."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import Ack
from ycli.yandex.wiki.grids import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.grids.models import (
        CellsUpdate,
        CellsUpdateResult,
        ColumnsAdd,
        ColumnsMove,
        ColumnsRemove,
        ColumnSuggest,
        ColumnSuggestion,
        ColumnUpdate,
        ColumnUpdateResult,
        Grid,
        GridClone,
        GridCreate,
        GridUpdate,
        RevisionResult,
        RowsAdd,
        RowsAddResult,
        RowsMove,
        RowsRemove,
        RowUpdate,
        RowUpdateResult,
    )
    from ycli.yandex.wiki.models import AsyncOperation


class GridsClient(Resource):
    """``/grids`` — dynamic tables (CRUD + rows/columns/cells + clone).

    Reads: :meth:`get`, :meth:`columns_suggest`. Writes: :meth:`create`, :meth:`update`,
    :meth:`delete`, the row/column add/remove/move calls, :meth:`cells_update`, the async
    :meth:`clone`, :meth:`columns_update` and :meth:`rows_update`.
    Every mutating body carries the ``revision`` the edit is based on, except ``create`` (no
    prior revision) and ``clone`` (a deferred trigger). The API refuses (409) only a cell
    changed after that revision; a stale one passes for every other write (checked live on
    2026-10-04).

    ``columns_suggest``, ``columns_update`` and ``rows_update`` call operations Yandex does not
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
        ``revision`` loads a historical version. Read the ``revision`` off the result and send it
        with the next write.

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
            endpoints.get(
                grid_id,
                fields=fields,
                row_filter=row_filter,
                only_cols=only_cols,
                only_rows=only_rows,
                revision=revision,
                sort=sort,
            )
        )

    def create(self, body: GridCreate) -> Grid:
        """``POST /grids`` — create a grid as a page resource. ``body`` is a ``GridCreate``.

        Args:
            body: The new grid: its title and the page it goes on.

        Returns:
            The created grid.

        Examples:
            >>> from ycli.yandex.wiki.grids.models import GridCreate
            >>> body = GridCreate.model_validate(
            ...     {"title": "Hiring plan", "page": {"slug": "hr/hiring"}}
            ... )
            >>> wiki.grids.create(body).title
            'Hiring plan'
        """
        return self._session.send(endpoints.create(body))

    def update(self, grid_id: str, body: GridUpdate) -> RevisionResult:
        """``POST /grids/{id}`` — rename / re-sort (POST not PATCH). ``body`` carries ``revision``.

        ``body`` is a ``GridUpdate``; its ``default_sort`` must use the *write* shape
        ``[{"<column_slug>": "asc"|"desc"}]`` — the ``{slug, title, direction}`` read shape
        returned by :meth:`get` is rejected with a 400.

        Args:
            grid_id: The grid's id.
            body: The changes, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> from ycli.yandex.wiki.grids.models import GridUpdate
            >>> body = GridUpdate.model_validate(
            ...     {
            ...         "revision": "12",
            ...         "title": "Roadmap 2027",
            ...         "default_sort": [{"due": "desc"}],
            ...     }
            ... )
            >>> wiki.grids.update(grid_id, body).revision
            '13'
        """
        return self._session.send(endpoints.update(grid_id, body))

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
        self._session.send(endpoints.delete(grid_id))
        return Ack.deleted("grid", grid_id)

    def rows_create(self, grid_id: str, body: RowsAdd) -> RowsAddResult:
        """``POST /grids/{id}/rows`` — insert rows. ``body`` is a ``RowsAdd`` (+ revision).

        Args:
            grid_id: The grid's id.
            body: The rows to add, with the grid's ``revision``.

        Returns:
            The grid's new revision and the added rows.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> rows = [{"name": "Launch", "owner": "vera"}]
            >>> from ycli.yandex.wiki.grids.models import RowsAdd
            >>> wiki.grids.rows_create(
            ...     grid_id, RowsAdd.model_validate({"revision": "13", "rows": rows})
            ... ).revision
            '14'
        """
        return self._session.send(endpoints.rows_create(grid_id, body))

    def rows_delete(self, grid_id: str, body: RowsRemove) -> RevisionResult:
        """``DELETE /grids/{id}/rows`` — delete rows by id. ``body`` is a ``RowsRemove``.

        A rare DELETE-with-body: ``row_ids`` + ``revision`` travel in the JSON body.

        Args:
            grid_id: The grid's id.
            body: The ids of the rows to delete, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> from ycli.yandex.wiki.grids.models import RowsRemove
            >>> wiki.grids.rows_delete(
            ...     grid_id, RowsRemove.model_validate({"revision": "14", "row_ids": ["r1", "r2"]})
            ... ).revision
            '15'
        """
        return self._session.send(endpoints.rows_delete(grid_id, body))

    def rows_move(self, grid_id: str, body: RowsMove) -> RevisionResult:
        """``POST /grids/{id}/rows/move`` — reorder rows. ``body`` is a ``RowsMove``.

        Args:
            grid_id: The grid's id.
            body: The row to move and where, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> from ycli.yandex.wiki.grids.models import RowsMove
            >>> wiki.grids.rows_move(
            ...     grid_id,
            ...     RowsMove.model_validate({"revision": "15", "row_id": "r3", "position": 4}),
            ... ).revision
            '16'
        """
        return self._session.send(endpoints.rows_move(grid_id, body))

    def columns_create(self, grid_id: str, body: ColumnsAdd) -> RevisionResult:
        """``POST /grids/{id}/columns`` — add columns. ``body`` is a ``ColumnsAdd``.

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
            >>> from ycli.yandex.wiki.grids.models import ColumnsAdd
            >>> wiki.grids.columns_create(
            ...     grid_id, ColumnsAdd.model_validate({"revision": "16", "columns": columns})
            ... ).revision
            '17'
        """
        return self._session.send(endpoints.columns_create(grid_id, body))

    def columns_delete(self, grid_id: str, body: ColumnsRemove) -> RevisionResult:
        """``DELETE /grids/{id}/columns`` — delete columns by slug. ``body`` is a ``ColumnsRemove``.

        A rare DELETE-with-body: ``column_slugs`` + ``revision`` travel in the JSON body.

        Args:
            grid_id: The grid's id.
            body: The slugs of the columns to delete, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> from ycli.yandex.wiki.grids.models import ColumnsRemove
            >>> body = ColumnsRemove.model_validate(
            ...     {"revision": "17", "column_slugs": ["stage", "due_date"]}
            ... )
            >>> wiki.grids.columns_delete(grid_id, body).revision
            '18'
        """
        return self._session.send(endpoints.columns_delete(grid_id, body))

    def columns_move(self, grid_id: str, body: ColumnsMove) -> RevisionResult:
        """``POST /grids/{id}/columns/move`` — reorder columns. ``body`` is a ``ColumnsMove`` dump.

        Args:
            grid_id: The grid's id.
            body: The column to move and where, with the grid's ``revision``.

        Returns:
            The grid's new revision.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> from ycli.yandex.wiki.grids.models import ColumnsMove
            >>> body = ColumnsMove.model_validate(
            ...     {"revision": "18", "column_slug": "owner", "position": 0}
            ... )
            >>> wiki.grids.columns_move(grid_id, body).revision
            '19'
        """
        return self._session.send(endpoints.columns_move(grid_id, body))

    def cells_update(self, grid_id: str, body: CellsUpdate) -> CellsUpdateResult:
        """``POST /grids/{id}/cells`` — set individual cell values. ``body`` is a ``CellsUpdate``.

        Args:
            grid_id: The grid's id.
            body: The cells to set, with the grid's ``revision``.

        Returns:
            The grid's new revision and the updated cells.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> cells = [{"row_id": 101, "column_slug": "name", "value": "Launch v2"}]
            >>> from ycli.yandex.wiki.grids.models import CellsUpdate
            >>> wiki.grids.cells_update(
            ...     grid_id, CellsUpdate.model_validate({"revision": "19", "cells": cells})
            ... ).revision
            '20'
        """
        return self._session.send(endpoints.cells_update(grid_id, body))

    def clone(self, grid_id: str, body: GridClone) -> AsyncOperation:
        """``POST /grids/{id}/clone`` — copy the grid onto another page (async trigger).

        Returns a :class:`~ycli.yandex.wiki.models.AsyncOperation`; poll its
        ``operation.id`` via ``OperationsClient.clone_inline_grid_get`` until terminal. ``body``
        is a ``GridClone`` (``{target, title?, with_data}``).

        Args:
            grid_id: The grid's id.
            body: The target page, an optional title and whether to copy the data.

        Returns:
            The clone operation to poll.

        Examples:
            >>> grid_id = "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01"
            >>> from ycli.yandex.wiki.grids.models import GridClone
            >>> body = GridClone.model_validate(
            ...     {"target": "eng/roadmap-copy", "title": "Roadmap copy", "with_data": True}
            ... )
            >>> wiki.grids.clone(grid_id, body).operation.id
            'task-6201'
        """
        return self._session.send(endpoints.clone(grid_id, body))

    def columns_suggest(self, grid_id: str, body: ColumnSuggest) -> ColumnSuggestion:
        """``POST /grids/{id}/columns/suggest`` — is a column slug free? (undocumented, may change).

        A read despite the POST: it changes nothing. ``body`` is a :class:`ColumnSuggest`
        (``{title?, slug?}``); a ``title`` is turned into a slug first. The reply says whether the
        slug is ``occupied`` and lists free alternatives.

        Args:
            grid_id: The grid's id.
            body: The column's ``title`` and/or ``slug``.

        Returns:
            Whether the slug is occupied, with free alternatives.

        Examples:
            >>> from ycli.yandex.wiki.grids.models import ColumnSuggest
            >>> wiki.grids.columns_suggest(
            ...     "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a02",
            ...     ColumnSuggest.model_validate({"title": "Due date"}),
            ... ).occupied
            False
        """
        return self._session.send(endpoints.columns_suggest(grid_id, body))

    def columns_update(
        self, grid_id: str, column_slug: str, body: ColumnUpdate
    ) -> ColumnUpdateResult:
        """``POST /grids/{id}/column/{slug}`` — edit a column in place (undocumented, may change).

        The only way to change a column after creating it; its ``type`` and ``slug`` stay. ``body``
        is a :class:`ColumnUpdate`: only the fields sent change. ``revision`` is accepted but
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
            >>> from ycli.yandex.wiki.grids.models import ColumnUpdate
            >>> wiki.grids.columns_update(
            ...     grid_id, "stage", ColumnUpdate.model_validate({"title": "Stage 2"})
            ... ).column.title
            'Stage 2'
        """
        return self._session.send(endpoints.columns_update(grid_id, column_slug, body))

    def rows_update(self, grid_id: str, row_id: str, body: RowUpdate) -> RowUpdateResult:
        """``POST /grids/{id}/rows/{row_id}`` — pin or colour one row (undocumented, may change).

        ``body`` is a :class:`RowUpdate` (``{revision?, pinned?, color?}``). The reply is a
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
            >>> from ycli.yandex.wiki.grids.models import RowUpdate
            >>> wiki.grids.rows_update(
            ...     grid_id, "103", RowUpdate.model_validate({"pinned": True, "color": "orange"})
            ... )
            RowUpdateResult(...)
        """
        return self._session.send(endpoints.rows_update(grid_id, row_id, body))
