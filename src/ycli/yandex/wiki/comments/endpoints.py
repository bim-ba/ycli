"""Wiki ``/pages/{id}/comments``, declared once (sans-IO).

Example:
    >>> delete_comment(7, 9).path
    'pages/7/comments/9'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.wiki.comments.models import (
    Comment,
    CommentCreated,
    CommentDeleteResult,
    CommentsResponse,
)
from ycli.yandex.wiki.cursor import WIKI_CURSOR


def list_comments(page_id: int) -> Paged[CommentsResponse, Comment]:
    path = f"pages/{segment(page_id)}/comments"
    return Paged(
        Endpoint("GET", path, CommentsResponse, params={"page_size": 100}),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def create_comment(page_id: int, body: dict[str, Any]) -> Endpoint[CommentCreated]:
    return Endpoint("POST", f"pages/{segment(page_id)}/comments", CommentCreated, json=body)


def delete_comment(page_id: int, comment_id: int) -> Endpoint[CommentDeleteResult]:
    path = f"pages/{segment(page_id)}/comments/{segment(comment_id)}"
    return Endpoint("DELETE", path, CommentDeleteResult)
