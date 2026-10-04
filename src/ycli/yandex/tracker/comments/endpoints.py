"""Tracker issue ``/comments`` operations, declared once (sans-IO).

Examples:
    >>> react("DE-1", 2238, "LIKE").path
    'issues/DE-1/comments/2238/reactions/LIKE'
    >>> list_("DE-1", expand=None, page_size=10).endpoint.params
    {'perPage': 10, 'expand': None}
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIDPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.comments.models import Comment, CommentUpdate

if TYPE_CHECKING:
    from ycli.yandex.tracker.models import CommentCreate

PAGE_SIZE = 100


def _comment_id(comment: Comment) -> str | None:
    return str(comment.id) if comment.id is not None else None


def list_(
    key: str, *, expand: str | None, page_size: int = PAGE_SIZE
) -> Paged[ItemList[Comment], Comment]:
    """``GET /issues/{key}/comments``, each next page from ``id=<last comment id>``."""
    return Paged(
        Endpoint(
            "GET",
            f"issues/{segment(key)}/comments",
            ItemList[Comment],
            params={"perPage": page_size, "expand": expand},
        ),
        RelativeIDPagination(id_of=_comment_id),
        lambda page: page.root,
    )


def get(key: str, comment_id: int | str, *, expand: str | None = None) -> Endpoint[Comment]:
    path = f"issues/{segment(key)}/comments/{segment(comment_id)}"
    return Endpoint("GET", path, Comment, params={"expand": expand})


def add(key: str, body: CommentCreate) -> Endpoint[Comment]:
    return Endpoint("POST", f"issues/{segment(key)}/comments/", Comment, json=body)


def update(key: str, comment_id: int | str, body: CommentUpdate) -> Endpoint[Comment]:
    path = f"issues/{segment(key)}/comments/{segment(comment_id)}"
    return Endpoint("PATCH", path, Comment, json=body)


def delete(key: str, comment_id: int | str) -> Endpoint[None]:
    return Endpoint("DELETE", f"issues/{segment(key)}/comments/{segment(comment_id)}")


def react(key: str, comment_id: int | str, name: str) -> Endpoint[Comment]:
    path = f"issues/{segment(key)}/comments/{segment(comment_id)}/reactions/{segment(name)}"
    return Endpoint("POST", path, Comment)
