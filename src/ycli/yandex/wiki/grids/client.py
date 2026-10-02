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

        ``fields`` adds optional blocks (``attributes``, ``user_permissions``); ``filter`` /
        ``only_cols`` / ``only_rows`` / ``sort`` narrow the returned rows and columns server-side;
        ``revision`` loads a historical version. Read the ``revision`` off the result to drive any
        subsequent write's optimistic lock.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.get("g-uuid").revision  # doctest: +SKIP
            '3'
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

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.create(
            ...     {"title": "Roadmap", "page": {"slug": "data/x"}}
            ... ).id  # doctest: +SKIP
            'g-uuid'
        """
        return self._session.send(endpoints.create_grid(body))

    def update(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``POST /grids/{id}`` — rename / re-sort (POST not PATCH). ``body`` carries ``revision``.

        ``body`` is a dumped ``GridUpdate``; its ``default_sort`` must use the *write* shape
        ``[{"<column_slug>": "asc"|"desc"}]`` — the ``{slug, title, direction}`` read shape
        returned by :meth:`get` is rejected with a 400.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.update(
            ...     "g-uuid", {"revision": "3", "default_sort": [{"col": "asc"}]}
            ... ).revision  # doctest: +SKIP
            '4'
        """
        return self._session.send(endpoints.update_grid(grid_id, body))

    def delete(self, grid_id: str) -> Ack:
        """``DELETE /grids/{id}`` → an :class:`Ack` (``204 No Content``).

        The API returns no body, so the result is synthesized; a non-2xx status raises a typed
        ``YandexError`` before this returns.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.delete("g-uuid").ok  # doctest: +SKIP
            True
        """
        self._session.send(endpoints.delete_grid(grid_id))
        return Ack.deleted("grid", grid_id)

    def add_rows(self, grid_id: str, body: dict[str, Any]) -> RowsAddResult:
        """``POST /grids/{id}/rows`` — insert rows. ``body`` is a dumped ``RowsAdd`` (+ revision).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.add_rows(
            ...     "g-uuid", {"revision": "3", "rows": [{"name": "x"}]}
            ... ).revision  # doctest: +SKIP
            '4'
        """
        return self._session.send(endpoints.add_rows(grid_id, body))

    def remove_rows(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``DELETE /grids/{id}/rows`` — delete rows by id. ``body`` is a dumped ``RowsRemove``.

        A rare DELETE-with-body: ``row_ids`` + ``revision`` travel in the JSON body.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.remove_rows(
            ...     "g-uuid", {"revision": "3", "row_ids": ["r1"]}
            ... ).revision  # doctest: +SKIP
            '4'
        """
        return self._session.send(endpoints.remove_rows(grid_id, body))

    def move_rows(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``POST /grids/{id}/rows/move`` — reorder rows. ``body`` is a dumped ``RowsMove``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.move_rows(
            ...     "g-uuid", {"revision": "3", "row_id": "r1", "position": 0}
            ... ).revision  # doctest: +SKIP
            '4'
        """
        return self._session.send(endpoints.move_rows(grid_id, body))

    def add_columns(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``POST /grids/{id}/columns`` — add columns. ``body`` is a dumped ``ColumnsAdd``.

        The API requires a ``slug`` on every column (400 ``value_error.missing`` without one);
        ``ColumnsAdd`` derives it from the title when omitted, but a raw dict body passed here
        directly must carry it.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.add_columns(
            ...     "g-uuid",
            ...     {"revision": "3", "columns": [{"title": "C", "type": "string", "slug": "c"}]},
            ... ).revision  # doctest: +SKIP
            '4'
        """
        return self._session.send(endpoints.add_columns(grid_id, body))

    def remove_columns(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``DELETE /grids/{id}/columns`` — delete columns by slug. ``body`` is a ``ColumnsRemove``.

        A rare DELETE-with-body: ``column_slugs`` + ``revision`` travel in the JSON body.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.remove_columns(
            ...     "g-uuid", {"revision": "3", "column_slugs": ["name"]}
            ... ).revision  # doctest: +SKIP
            '4'
        """
        return self._session.send(endpoints.remove_columns(grid_id, body))

    def move_columns(self, grid_id: str, body: dict[str, Any]) -> RevisionResult:
        """``POST /grids/{id}/columns/move`` — reorder columns. ``body`` is a ``ColumnsMove`` dump.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.move_columns(
            ...     "g-uuid", {"revision": "3", "column_slug": "name", "position": 0}
            ... ).revision  # doctest: +SKIP
            '4'
        """
        return self._session.send(endpoints.move_columns(grid_id, body))

    def update_cells(self, grid_id: str, body: dict[str, Any]) -> CellsUpdateResult:
        """``POST /grids/{id}/cells`` — set individual cell values. ``body`` is a ``CellsUpdate``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.update_cells(
            ...     "g-uuid",
            ...     {
            ...         "revision": "3",
            ...         "cells": [{"row_id": 1, "column_slug": "name", "value": "x"}],
            ...     },
            ... ).revision  # doctest: +SKIP
            '4'
        """
        return self._session.send(endpoints.update_cells(grid_id, body))

    def clone(self, grid_id: str, body: dict[str, Any]) -> GridCloneOperation:
        """``POST /grids/{id}/clone`` — copy the grid onto another page (async trigger).

        Returns a :class:`~ycli.yandex.wiki.grids.models.GridCloneOperation`; poll its
        ``operation.id`` via ``OperationsClient.gridclone_get`` until terminal. ``body`` is a
        dumped ``GridClone`` (``{target, title?, with_data}``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.clone("g-uuid", {"target": "data/y"}).operation.id  # doctest: +SKIP
            'task-1'
        """
        return self._session.send(endpoints.clone_grid(grid_id, body))

    def suggest_column(self, grid_id: str, body: dict[str, Any]) -> ColumnSuggestion:
        """``POST /grids/{id}/columns/suggest`` — is a column slug free? (undocumented, may change).

        A read despite the POST: it changes nothing. ``body`` is a dumped :class:`ColumnSuggest`
        (``{title?, slug?}``); a ``title`` is turned into a slug first. The reply says whether the
        slug is ``occupied`` and lists free alternatives.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.suggest_column("g-uuid", {"title": "Owner"}).occupied  # doctest: +SKIP
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

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.update_column(
            ...     "g-uuid", "owner", {"revision": "3", "title": "Lead"}
            ... ).column.title  # doctest: +SKIP
            'Lead'
        """
        return self._session.send(endpoints.update_column(grid_id, column_slug, body))

    def update_row(self, grid_id: str, row_id: str, body: dict[str, Any]) -> RowUpdateResult:
        """``POST /grids/{id}/rows/{row_id}`` — pin or colour one row (undocumented, may change).

        ``body`` is a dumped :class:`RowUpdate` (``{revision?, pinned?, color?}``). The reply is a
        bare acknowledgement without the new revision (read it with :meth:`get`); ``revision`` is
        accepted but not enforced, and every call moves the grid's revision on.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.update_row(
            ...     "g-uuid", "7", {"revision": "3", "pinned": True}
            ... ).status  # doctest: +SKIP
            'ok'
        """
        return self._session.send(endpoints.update_row(grid_id, row_id, body))
