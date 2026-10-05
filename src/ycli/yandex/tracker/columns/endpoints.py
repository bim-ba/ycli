"""Tracker board ``/columns`` operations, declared once (sans-IO).

Examples:
    >>> get(73, 5).path
    'boards/73/columns/5'
    >>> delete(73, 5).effect
    <Effect.DESTRUCTIVE: 'destructive'>
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.columns.models import Column, ColumnCreate, ColumnUpdate


def list_(board_id: int) -> Endpoint[ItemList[Column]]:
    return Endpoint(HTTPMethod.GET, f"boards/{segment(board_id)}/columns", ItemList[Column])


def get(board_id: int, column_id: int) -> Endpoint[Column]:
    return Endpoint(
        HTTPMethod.GET, f"boards/{segment(board_id)}/columns/{segment(column_id)}", Column
    )


def create(board_id: int, body: ColumnCreate) -> Endpoint[Column]:
    return Endpoint(HTTPMethod.POST, f"boards/{segment(board_id)}/columns/", Column, json=body)


def update(board_id: int, column_id: int, body: ColumnUpdate) -> Endpoint[Column]:
    path = f"boards/{segment(board_id)}/columns/{segment(column_id)}"
    return Endpoint(HTTPMethod.PATCH, path, Column, json=body)


def delete(board_id: int, column_id: int) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, f"boards/{segment(board_id)}/columns/{segment(column_id)}")
