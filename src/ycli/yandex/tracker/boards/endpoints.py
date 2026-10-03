"""Tracker ``/boards`` operations, declared once (sans-IO).

Examples:
    >>> get_board(7).path
    'boards/7'
    >>> list_boards(page_size=20).endpoint.params
    {'perPage': 20}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIdPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.boards.models import Board

PAGE_SIZE = 100


def _board_id(board: Board) -> str | None:
    return str(board.id) if board.id is not None else None


def list_boards(*, page_size: int = PAGE_SIZE) -> Paged[ItemList[Board], Board]:
    """``GET /boards/_paginate``: ascending ids, each next page from ``id=<last board id>``."""
    return Paged(
        Endpoint("GET", "boards/_paginate", ItemList[Board], params={"perPage": page_size}),
        RelativeIdPagination(id_of=_board_id),
        lambda page: page.root,
    )


def get_board(board_id: int) -> Endpoint[Board]:
    return Endpoint("GET", f"boards/{segment(board_id)}", Board)


def create_board(body: dict[str, Any]) -> Endpoint[Board]:
    """``POST /liveBoards/``: the older ``POST /boards/`` silently ignores the body."""
    return Endpoint("POST", "liveBoards/", Board, json=body)


def edit_board(board_id: int, body: dict[str, Any]) -> Endpoint[Board]:
    return Endpoint("PATCH", f"boards/{segment(board_id)}", Board, json=body)


def delete_board(board_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"boards/{segment(board_id)}")
