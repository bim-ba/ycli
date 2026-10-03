"""Pydantic models for Tracker issue comments (Comment + ItemList[Comment])."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)
from ycli.yandex.tracker.models import Reference


class Comment(APIModel):
    """A Tracker issue comment (``/issues/{key}/comments`` item).

    Examples:
        >>> Comment.model_validate({"id": 2238, "createdBy": {"display": "X"}, "text": "t"}).id
        2238
    """

    id: int | str | None = None
    long_id: str | None = Field(default=None, alias="longId")
    created_at: str | None = Field(default=None, alias="createdAt")
    created_by: DisplayStr = Field(default=None, alias="createdBy")
    updated_at: str | None = Field(default=None, alias="updatedAt")
    updated_by: DisplayStr = Field(default=None, alias="updatedBy")
    text: str | None = None
    text_html: str | None = Field(default=None, alias="textHtml")
    attachments: list[Reference] | None = None
    version: int | None = None
    type: str | None = None
    transport: str | None = None


class CommentUpdate(APIModel):
    """Typed request body for ``PATCH /issues/{key}/comments/{id}`` (edit a comment).

    Examples:
        >>> CommentUpdate(text="fixed ✅").model_dump(exclude_none=True)
        {'text': 'fixed ✅'}
    """

    text: str = Field(description="Corrected comment text (YFM markdown supported).")
