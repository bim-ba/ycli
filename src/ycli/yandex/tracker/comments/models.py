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


class CommentCreate(APIModel):
    """Typed request body for ``POST /issues/{key}/comments/`` (add a comment).

    Example:
        >>> CommentCreate(text="Готово ✅").model_dump(by_alias=True, exclude_none=True)
        {'text': 'Готово ✅'}
    """

    text: str = Field(description="Comment text (YFM markdown supported; required).")
    summonees: list[str] | None = Field(
        default=None, description="User ids/logins to summon in the comment."
    )
    attachment_ids: list[str] | None = Field(
        default=None, alias="attachmentIds", description="Temp-file ids to attach as files."
    )
    maillist_summonees: list[str] | None = Field(
        default=None, alias="maillistSummonees", description="Mailing lists to summon."
    )


class CommentUpdate(APIModel):
    """Typed request body for ``PATCH /issues/{key}/comments/{id}`` (edit a comment).

    Example:
        >>> CommentUpdate(text="fixed ✅").model_dump(exclude_none=True)
        {'text': 'fixed ✅'}
    """

    text: str = Field(description="Corrected comment text (YFM markdown supported).")
