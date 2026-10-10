"""Tracker ``/boards`` operations, declared once (sans-IO).

Examples:
    >>> get(7).path
    'boards/7'
    >>> list_(page_size=20).pagination.page_size
    20
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIDPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.boards.models import Board, BoardCreate, BoardUpdate

PAGE_SIZE = 100


def _board_id(board: Board) -> str | None:
    return str(board.id) if board.id is not None else None


def list_(*, page_size: int = PAGE_SIZE) -> Paged[ItemList[Board], Board]:
    """``GET /boards/_paginate``: ascending ids, each next page from ``id=<last board id>``."""
    return Paged(
        Endpoint(HTTPMethod.GET, "boards/_paginate", ItemList[Board]),
        RelativeIDPagination(id_of=_board_id, page_size=page_size),
        lambda page: page.root,
    )


def get(board_id: int) -> Endpoint[Board]:
    return Endpoint(HTTPMethod.GET, f"boards/{segment(board_id)}", Board)


def create(body: BoardCreate) -> Endpoint[Board]:
    """``POST /liveBoards/``: the older ``POST /boards/`` silently ignores the body."""
    return Endpoint(HTTPMethod.POST, "liveBoards/", Board, json=body)


def update(board_id: int, body: BoardUpdate) -> Endpoint[Board]:
    return Endpoint(HTTPMethod.PATCH, f"boards/{segment(board_id)}", Board, json=body)


def delete(board_id: int) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, f"boards/{segment(board_id)}")
