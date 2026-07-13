"""Declarative Yandex Wiki /grids client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.models import Ack
from ycli.yandex.wiki.base import WikiResource
from ycli.yandex.wiki.grids.models import (
    CellsUpdateResult,
    Grid,
    GridCloneOperation,
    RevisionResult,
    RowsAddResult,
)


class GridsClient(WikiResource):
    """Declarative HTTP for ``/grids`` — dynamic tables (CRUD + rows/columns/cells + clone).

    Reads: :meth:`get`. Writes (SDK/CLI only): :meth:`create`, :meth:`update`, :meth:`delete`,
    the row/column add/remove/move calls, :meth:`update_cells`, and the async :meth:`clone`.
    Every mutating body carries a ``revision`` for optimistic locking except ``create`` (no prior
    revision) and ``clone`` (a deferred trigger).
    """

    @uplink.returns.json()
    @uplink.get("grids/{grid_id}")
    def get(
        self,
        grid_id: uplink.Path,
        fields: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        row_filter: uplink.Query("filter") = None,  # ty: ignore[invalid-type-form]
        only_cols: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        only_rows: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        revision: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        sort: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> Grid:  # ty: ignore[empty-body]
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

    @uplink.returns.json()
    @uplink.json
    @uplink.post("grids")
    def create(self, body: uplink.Body) -> Grid:  # ty: ignore[empty-body]
        """``POST /grids`` — create a grid as a page resource. ``body`` is a dumped ``GridCreate``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.create(
            ...     {"title": "Roadmap", "page": {"slug": "data/x"}}
            ... ).id  # doctest: +SKIP
            'g-uuid'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("grids/{grid_id}")
    def update(self, grid_id: uplink.Path, body: uplink.Body) -> RevisionResult:  # ty: ignore[empty-body]
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

    @uplink.delete("grids/{grid_id}")
    def _delete(self, grid_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """Raw ``DELETE /grids/{id}`` (204 No Content); internal — callers use ``delete``."""

    def delete(self, grid_id: str) -> Ack:
        """``DELETE /grids/{id}`` → an :class:`Ack` (``204 No Content``).

        The API returns no body, so the result is synthesized; a non-2xx status raises a typed
        ``YandexError`` before this returns.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.delete("g-uuid").ok  # doctest: +SKIP
            True
        """
        self._delete(grid_id)
        return Ack.deleted("grid", grid_id)

    @uplink.returns.json()
    @uplink.json
    @uplink.post("grids/{grid_id}/rows")
    def add_rows(self, grid_id: uplink.Path, body: uplink.Body) -> RowsAddResult:  # ty: ignore[empty-body]
        """``POST /grids/{id}/rows`` — insert rows. ``body`` is a dumped ``RowsAdd`` (+ revision).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.add_rows(
            ...     "g-uuid", {"revision": "3", "rows": [{"name": "x"}]}
            ... ).revision  # doctest: +SKIP
            '4'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.delete("grids/{grid_id}/rows")
    def remove_rows(self, grid_id: uplink.Path, body: uplink.Body) -> RevisionResult:  # ty: ignore[empty-body]
        """``DELETE /grids/{id}/rows`` — delete rows by id. ``body`` is a dumped ``RowsRemove``.

        A rare DELETE-with-body: ``row_ids`` + ``revision`` travel in the JSON body.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.remove_rows(
            ...     "g-uuid", {"revision": "3", "row_ids": ["r1"]}
            ... ).revision  # doctest: +SKIP
            '4'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("grids/{grid_id}/rows/move")
    def move_rows(self, grid_id: uplink.Path, body: uplink.Body) -> RevisionResult:  # ty: ignore[empty-body]
        """``POST /grids/{id}/rows/move`` — reorder rows. ``body`` is a dumped ``RowsMove``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.move_rows(
            ...     "g-uuid", {"revision": "3", "row_id": "r1", "position": 0}
            ... ).revision  # doctest: +SKIP
            '4'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("grids/{grid_id}/columns")
    def add_columns(self, grid_id: uplink.Path, body: uplink.Body) -> RevisionResult:  # ty: ignore[empty-body]
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

    @uplink.returns.json()
    @uplink.json
    @uplink.delete("grids/{grid_id}/columns")
    def remove_columns(self, grid_id: uplink.Path, body: uplink.Body) -> RevisionResult:  # ty: ignore[empty-body]
        """``DELETE /grids/{id}/columns`` — delete columns by slug. ``body`` is a ``ColumnsRemove``.

        A rare DELETE-with-body: ``column_slugs`` + ``revision`` travel in the JSON body.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.remove_columns(
            ...     "g-uuid", {"revision": "3", "column_slugs": ["name"]}
            ... ).revision  # doctest: +SKIP
            '4'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("grids/{grid_id}/columns/move")
    def move_columns(self, grid_id: uplink.Path, body: uplink.Body) -> RevisionResult:  # ty: ignore[empty-body]
        """``POST /grids/{id}/columns/move`` — reorder columns. ``body`` is a ``ColumnsMove`` dump.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.move_columns(
            ...     "g-uuid", {"revision": "3", "column_slug": "name", "position": 0}
            ... ).revision  # doctest: +SKIP
            '4'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("grids/{grid_id}/cells")
    def update_cells(self, grid_id: uplink.Path, body: uplink.Body) -> CellsUpdateResult:  # ty: ignore[empty-body]
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

    @uplink.returns.json()
    @uplink.json
    @uplink.post("grids/{grid_id}/clone")
    def clone(self, grid_id: uplink.Path, body: uplink.Body) -> GridCloneOperation:  # ty: ignore[empty-body]
        """``POST /grids/{id}/clone`` — copy the grid onto another page (async trigger).

        Returns a :class:`~ycli.yandex.wiki.grids.models.GridCloneOperation`; poll its
        ``operation.id`` via ``OperationsClient.gridclone_get`` until terminal. ``body`` is a
        dumped ``GridClone`` (``{target, title?, with_data}``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.grids.clone("g-uuid", {"target": "data/y"}).operation.id  # doctest: +SKIP
            'task-1'
        """
