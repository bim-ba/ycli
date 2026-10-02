"""Wiki ``/grids`` — dynamic tables, declared once (sans-IO).

The API updates a grid and sets cell values with ``POST`` (not ``PATCH``); the same body sent
twice leaves the same grid, so those two endpoints declare themselves idempotent writes. Rows and
columns are removed by a ``DELETE`` whose ids travel in the JSON body.

Example:
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

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.wiki.grids.models import (
    CellsUpdateResult,
    Grid,
    GridCloneOperation,
    RevisionResult,
    RowsAddResult,
)


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


def create_grid(body: dict[str, Any]) -> Endpoint[Grid]:
    return Endpoint("POST", "grids", Grid, json=body)


def update_grid(grid_id: str, body: dict[str, Any]) -> Endpoint[RevisionResult]:
    return Endpoint("POST", _grid(grid_id), RevisionResult, json=body, effect="idempotent_write")


def delete_grid(grid_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", _grid(grid_id))


def add_rows(grid_id: str, body: dict[str, Any]) -> Endpoint[RowsAddResult]:
    return Endpoint("POST", _grid(grid_id, "/rows"), RowsAddResult, json=body)


def remove_rows(grid_id: str, body: dict[str, Any]) -> Endpoint[RevisionResult]:
    return Endpoint("DELETE", _grid(grid_id, "/rows"), RevisionResult, json=body)


def move_rows(grid_id: str, body: dict[str, Any]) -> Endpoint[RevisionResult]:
    return Endpoint("POST", _grid(grid_id, "/rows/move"), RevisionResult, json=body)


def add_columns(grid_id: str, body: dict[str, Any]) -> Endpoint[RevisionResult]:
    return Endpoint("POST", _grid(grid_id, "/columns"), RevisionResult, json=body)


def remove_columns(grid_id: str, body: dict[str, Any]) -> Endpoint[RevisionResult]:
    return Endpoint("DELETE", _grid(grid_id, "/columns"), RevisionResult, json=body)


def move_columns(grid_id: str, body: dict[str, Any]) -> Endpoint[RevisionResult]:
    return Endpoint("POST", _grid(grid_id, "/columns/move"), RevisionResult, json=body)


def update_cells(grid_id: str, body: dict[str, Any]) -> Endpoint[CellsUpdateResult]:
    path = _grid(grid_id, "/cells")
    return Endpoint("POST", path, CellsUpdateResult, json=body, effect="idempotent_write")


def clone_grid(grid_id: str, body: dict[str, Any]) -> Endpoint[GridCloneOperation]:
    return Endpoint("POST", _grid(grid_id, "/clone"), GridCloneOperation, json=body)
