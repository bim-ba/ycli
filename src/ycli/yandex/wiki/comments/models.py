"""Pydantic v2 models for Yandex Wiki /pages/{id}/comments responses (extra='ignore')."""
from __future__ import annotations

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

    Example:
        >>> CommentsResponse.model_validate({"results": [{"content": "ok"}]}).results[0].content
        'ok'
    """

    results: list[Comment] = []
