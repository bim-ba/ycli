"""Pydantic v2 models for Yandex Wiki /pages/{id}/comments responses (extra='ignore')."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class Comment(APIModel):
    """A wiki page comment (``/pages/{id}/comments`` item).

    Example:
        >>> Comment.model_validate({"author": {"display": "Сава"}, "content": "ok"}).author
        'Сава'
    """

    created_at: str | None = None
    author: DisplayStr = None
    content: str | None = None


class CommentsResponse(APIModel):
    """Envelope for ``GET /pages/{id}/comments`` — ``{results:[Comment]}``.

    Internal per-page parse type used by ``CommentsClient._list_page``.

    Example:
        >>> CommentsResponse.model_validate({"results": [{"content": "ok"}]}).results[0].content
        'ok'
    """

    results: list[Comment] = Field(default_factory=list)


class CommentList(RootModel[list[Comment]]):
    """Flat collection of :class:`Comment` items — public return type of ``CommentsClient.list``.

    Example:
        >>> CommentList([Comment.model_validate({"content": "ok"})]).root[0].content
        'ok'
    """

    root: list[Comment] = Field(default_factory=list)
