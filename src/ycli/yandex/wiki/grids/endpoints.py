"""Wiki ``/grids`` — dynamic tables, declared once (sans-IO).

The API updates a grid and sets cell values with ``POST`` (not ``PATCH``); the same body sent
twice leaves the same grid, so those two endpoints declare themselves idempotent writes. Rows and
columns are removed by a ``DELETE`` whose ids travel in the JSON body.

Examples:
    >>> get_grid(
    ...     "g-1",
    ...     fields=None,
    ...     row_filter="[a] ~ b",
    ...     only_cols=None,
    ...     only_rows=None,
    ...     revision=None,
    ...     sort=None,
    ... ).params["filter"]
    '[a] ~ b'
    >>> update_cells("g-1", {"revision": "3", "cells": []}).effect
    'idempotent_write'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
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


def _grid(grid_id: str, tail: str = "") -> str:
    return f"grids/{segment(grid_id)}{tail}"


def get_grid(
    grid_id: str,
    *,
    fields: str | None,
    row_filter: str | None,
    only_cols: str | None,
    only_rows: str | None,
    revision: str | None,
    sort: str | None,
) -> Endpoint[Grid]:
    params = {
        "fields": fields,
        "filter": row_filter,
        "only_cols": only_cols,
        "only_rows": only_rows,
        "revision": revision,
        "sort": sort,
    }
    return Endpoint("GET", _grid(grid_id), Grid, params=params)


def create_grid(body: GridCreate) -> Endpoint[Grid]:
    return Endpoint("POST", "grids", Grid, json=body)


def update_grid(grid_id: str, body: GridUpdate) -> Endpoint[RevisionResult]:
    return Endpoint("POST", _grid(grid_id), RevisionResult, json=body, effect="idempotent_write")


def delete_grid(grid_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", _grid(grid_id))


def add_rows(grid_id: str, body: RowsAdd) -> Endpoint[RowsAddResult]:
    return Endpoint("POST", _grid(grid_id, "/rows"), RowsAddResult, json=body)


def remove_rows(grid_id: str, body: RowsRemove) -> Endpoint[RevisionResult]:
    return Endpoint("DELETE", _grid(grid_id, "/rows"), RevisionResult, json=body)


def move_rows(grid_id: str, body: RowsMove) -> Endpoint[RevisionResult]:
    return Endpoint("POST", _grid(grid_id, "/rows/move"), RevisionResult, json=body)


def add_columns(grid_id: str, body: ColumnsAdd) -> Endpoint[RevisionResult]:
    return Endpoint("POST", _grid(grid_id, "/columns"), RevisionResult, json=body)


def remove_columns(grid_id: str, body: ColumnsRemove) -> Endpoint[RevisionResult]:
    return Endpoint("DELETE", _grid(grid_id, "/columns"), RevisionResult, json=body)


def move_columns(grid_id: str, body: ColumnsMove) -> Endpoint[RevisionResult]:
    return Endpoint("POST", _grid(grid_id, "/columns/move"), RevisionResult, json=body)


def update_cells(grid_id: str, body: CellsUpdate) -> Endpoint[CellsUpdateResult]:
    path = _grid(grid_id, "/cells")
    return Endpoint("POST", path, CellsUpdateResult, json=body, effect="idempotent_write")


def clone_grid(grid_id: str, body: GridClone) -> Endpoint[AsyncOperation]:
    return Endpoint("POST", _grid(grid_id, "/clone"), AsyncOperation, json=body)


def suggest_column(grid_id: str, body: ColumnSuggest) -> Endpoint[ColumnSuggestion]:
    """``POST /grids/{id}/columns/suggest`` (undocumented): checks a slug, changes nothing."""
    path = _grid(grid_id, "/columns/suggest")
    return Endpoint("POST", path, ColumnSuggestion, json=body, effect="read")


def update_column(
    grid_id: str, column_slug: str, body: ColumnUpdate
) -> Endpoint[ColumnUpdateResult]:
    """``POST /grids/{id}/column/{slug}`` (undocumented; the path says ``column``, singular)."""
    path = _grid(grid_id, f"/column/{segment(column_slug)}")
    return Endpoint("POST", path, ColumnUpdateResult, json=body, effect="idempotent_write")


def update_row(grid_id: str, row_id: str, body: RowUpdate) -> Endpoint[RowUpdateResult]:
    """``POST /grids/{id}/rows/{row_id}`` (undocumented): pin or colour one row."""
    path = _grid(grid_id, f"/rows/{segment(row_id)}")
    return Endpoint("POST", path, RowUpdateResult, json=body, effect="idempotent_write")
