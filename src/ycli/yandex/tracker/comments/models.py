"""Pydantic models for Tracker issue comments (Comment + CommentList)."""
from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.tracker._models import _DisplayRef, _Lenient


class Comment(_Lenient):
    """A Tracker issue comment (``/issues/{key}/comments`` item).

    Example:
        >>> Comment.model_validate({"id": 2238, "createdBy": {"display": "X"}, "text": "t"}).id
        2238
    """

    id: int | str | None = None
    created_at: str | None = Field(default=None, alias="createdAt")
    created_by: _DisplayRef | None = Field(default=None, alias="createdBy")
    text: str | None = None

    @property
    def created_by_display(self) -> str | None:
        """``createdBy.display`` or ``None``."""
        return self.created_by.display if self.created_by else None


class CommentList(RootModel[list[Comment]]):
    """A bare JSON array of comments.

    Example:
        >>> CommentList.model_validate([{"text": "hi"}]).root[0].text
        'hi'
    """
