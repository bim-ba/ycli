"""Pydantic v2 models for Yandex Wiki /pages/{id}/comments responses (extra='ignore')."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Lenient(BaseModel):
    model_config = ConfigDict(extra="ignore")


class _CommentAuthor(_Lenient):
    display: str | None = None


class Comment(_Lenient):
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


class CommentsResponse(_Lenient):
    """Envelope for ``GET /pages/{id}/comments`` — ``{results:[Comment]}``.

    Example:
        >>> CommentsResponse.model_validate({"results": [{"content": "ok"}]}).results[0].content
        'ok'
    """

    results: list[Comment] = []
