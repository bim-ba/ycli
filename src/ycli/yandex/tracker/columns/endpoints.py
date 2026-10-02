"""Tracker board ``/columns`` operations, declared once (sans-IO).

Example:
    >>> get_column(73, 5).path
    'boards/73/columns/5'
    >>> delete_column(73, 5).effect
    'destructive'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.columns.models import Column, ColumnList


def list_columns(board_id: int) -> Endpoint[ColumnList]:
    return Endpoint("GET", f"boards/{segment(board_id)}/columns", ColumnList)


def get_column(board_id: int, column_id: int) -> Endpoint[Column]:
    return Endpoint("GET", f"boards/{segment(board_id)}/columns/{segment(column_id)}", Column)


def create_column(board_id: int, body: dict[str, Any]) -> Endpoint[Column]:
    return Endpoint("POST", f"boards/{segment(board_id)}/columns/", Column, json=body)


def edit_column(board_id: int, column_id: int, body: dict[str, Any]) -> Endpoint[Column]:
    path = f"boards/{segment(board_id)}/columns/{segment(column_id)}"
    return Endpoint("PATCH", path, Column, json=body)


def delete_column(board_id: int, column_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"boards/{segment(board_id)}/columns/{segment(column_id)}")
