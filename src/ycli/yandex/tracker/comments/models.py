"""Pydantic models for Tracker issue comments (Comment + CommentList)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class Comment(APIModel):
    """A Tracker issue comment (``/issues/{key}/comments`` item).

    Example:
        >>> Comment.model_validate({"id": 2238, "createdBy": {"display": "X"}, "text": "t"}).id
        2238
    """

    id: int | str | None = None
    created_at: str | None = Field(default=None, alias="createdAt")
    created_by: DisplayStr = Field(default=None, alias="createdBy")
    text: str | None = None


class CommentList(RootModel[list[Comment]]):
    """A bare JSON array of comments.

    Example:
        >>> CommentList.model_validate([{"text": "hi"}]).root[0].text
        'hi'
    """


class CommentUpdate(APIModel):
    """Typed request body for ``PATCH /issues/{key}/comments/{id}`` (edit a comment).

    Example:
        >>> CommentUpdate(text="fixed ✅").model_dump(exclude_none=True)
        {'text': 'fixed ✅'}
    """

    text: str = Field(description="Corrected comment text (YFM markdown supported).")
