"""Pydantic v2 models for Yandex Wiki /pages/{id}/comments responses (extra='ignore')."""
from __future__ import annotations

from pydantic import RootModel

from ycli.models import APIModel


class _CommentAuthor(APIModel):
    display: str | None = None


class Comment(APIModel):
    """A wiki page comment (``/pages/{id}/comments`` item).

    Example:
        >>> Comment.model_validate({"author": {"display": "Сава"}, "content": "ok"}).author_display
        'Сава'
    """

    created_at: str | None = None
    author: _CommentAuthor | None = None
    content: str | None = None

    @property
    def author_display(self) -> str | None:
        return self.author.display if self.author else None


class CommentsResponse(APIModel):
    """Envelope for ``GET /pages/{id}/comments`` — ``{results:[Comment]}``.

    Internal per-page parse type used by ``CommentsClient._list_page``.

    Example:
        >>> CommentsResponse.model_validate({"results": [{"content": "ok"}]}).results[0].content
        'ok'
    """

    results: list[Comment] = []


class CommentList(RootModel[list[Comment]]):
    """Flat collection of :class:`Comment` items — the public return type of ``CommentsClient.list``.

    Example:
        >>> CommentList([Comment.model_validate({"content": "ok"})]).root[0].content
        'ok'
    """

    root: list[Comment] = []
