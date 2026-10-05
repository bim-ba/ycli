"""Wiki ``/pages/{id}/comments``, declared once (sans-IO).

Examples:
    >>> delete(7, 9).path
    'pages/7/comments/9'
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.wiki.comments.models import (
    Comment,
    CommentCreate,
    CommentCreated,
    CommentDeleteResult,
)
from ycli.yandex.wiki.cursor import WIKI_CURSOR
from ycli.yandex.wiki.models import CursorPage


def list_(
    page_id: int, *, order_by: str | None, order_direction: str | None, status_filter: str | None
) -> Paged[CursorPage[Comment], Comment]:
    path = f"pages/{segment(page_id)}/comments"
    params = {
        "page_size": 100,
        "order_by": order_by,
        "order_direction": order_direction,
        "status_filter": status_filter,
    }
    return Paged(
        Endpoint(HTTPMethod.GET, path, CursorPage[Comment], params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def thread_get(page_id: int, comment_id: int) -> Paged[CursorPage[Comment], Comment]:
    path = f"pages/{segment(page_id)}/comments/{segment(comment_id)}/thread"
    return Paged(
        Endpoint(HTTPMethod.GET, path, CursorPage[Comment], params={"page_size": 100}),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def create(page_id: int, body: CommentCreate) -> Endpoint[CommentCreated]:
    return Endpoint(
        HTTPMethod.POST, f"pages/{segment(page_id)}/comments", CommentCreated, json=body
    )


def delete(page_id: int, comment_id: int) -> Endpoint[CommentDeleteResult]:
    path = f"pages/{segment(page_id)}/comments/{segment(comment_id)}"
    return Endpoint(HTTPMethod.DELETE, path, CommentDeleteResult)
