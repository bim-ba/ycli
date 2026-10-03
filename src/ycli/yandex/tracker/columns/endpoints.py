"""Tracker board ``/columns`` operations, declared once (sans-IO).

Examples:
    >>> get_column(73, 5).path
    'boards/73/columns/5'
    >>> delete_column(73, 5).effect
    'destructive'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.columns.models import Column, ColumnCreate, ColumnUpdate


def list_columns(board_id: int) -> Endpoint[ItemList[Column]]:
    return Endpoint("GET", f"boards/{segment(board_id)}/columns", ItemList[Column])


def get_column(board_id: int, column_id: int) -> Endpoint[Column]:
    return Endpoint("GET", f"boards/{segment(board_id)}/columns/{segment(column_id)}", Column)


def create_column(board_id: int, body: ColumnCreate) -> Endpoint[Column]:
    return Endpoint("POST", f"boards/{segment(board_id)}/columns/", Column, json=body)


def update_column(board_id: int, column_id: int, body: ColumnUpdate) -> Endpoint[Column]:
    path = f"boards/{segment(board_id)}/columns/{segment(column_id)}"
    return Endpoint("PATCH", path, Column, json=body)


def delete_column(board_id: int, column_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"boards/{segment(board_id)}/columns/{segment(column_id)}")
