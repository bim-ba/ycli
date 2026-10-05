"""Pydantic models for Tracker issue comments (Comment + ItemList[Comment])."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import (
    APIModel,
    DisplayStr,
    RequestBody,  # pydantic resolves field types via get_type_hints() at runtime
)
from ycli.yandex.tracker.models import Reference

#: The reaction names ``POST …/comments/{id}/reactions/{name}`` documents.
Reaction = (
    Literal[
        "LIKE",
        "DISLIKE",
        "LAUGH",
        "HOORAY",
        "CONFUSED",
        "HEART",
        "ROCKET",
        "EYES",
        "FIRE",
        "OK",
        "FACEPALM",
        "CHECK",
    ]
    | str
)


class Comment(APIModel):
    """A Tracker issue comment (``/issues/{key}/comments`` item).

    Examples:
        >>> Comment.model_validate({"id": 2238, "createdBy": {"display": "X"}, "text": "t"}).id
        2238
    """

    id: int | str | None = Field(default=None, description="Comment identifier.")
    long_id: str | None = Field(
        default=None, alias="longId", description="Comment identifier as a string."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="When the comment was created (ISO 8601)."
    )
    created_by: DisplayStr = Field(
        default=None, alias="createdBy", description="Display name of the comment author."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="When the comment was last updated (ISO 8601)."
    )
    updated_by: DisplayStr = Field(
        default=None,
        alias="updatedBy",
        description="Display name of the user who last updated the comment.",
    )
    text: str | None = Field(default=None, description="Comment text.")
    text_html: str | None = Field(
        default=None, alias="textHtml", description="Comment text as HTML markup."
    )
    attachments: list[Reference] | None = Field(
        default=None, description="Files attached to the comment."
    )
    version: int | None = Field(
        default=None, description="Comment version; every edit increments it."
    )
    type: str | None = Field(
        default=None,
        description="Comment type: ``standard``, ``incoming`` or ``outcoming``.",
    )
    transport: str | None = Field(
        default=None,
        description="How the comment was added: ``internal`` (Tracker interface) or ``email``.",
    )


class CommentUpdate(RequestBody):
    """Typed request body for ``PATCH /issues/{key}/comments/{id}`` (edit a comment).

    Examples:
        >>> CommentUpdate(text="fixed ✅").model_dump(exclude_none=True)
        {'text': 'fixed ✅'}
    """

    text: str = Field(description="Corrected comment text (YFM markdown supported).")


class ImportComment(RequestBody):
    """Typed body for ``POST /issues/{key}/comments/_import`` — import one comment with history.

    Examples:
        >>> ImportComment(
        ...     text="Test", created_at="2017-08-29T12:34:41.740+0000", created_by="11"
        ... ).model_dump(exclude_none=True)  # doctest: +NORMALIZE_WHITESPACE
        {'text': 'Test', 'createdAt': '2017-08-29T12:34:41.740+0000', 'createdBy': '11'}
    """

    text: str = Field(description="Comment text (max 512000 characters).")
    created_at: str = Field(alias="createdAt", description="Original comment creation time.")
    created_by: str = Field(alias="createdBy", description="Login or id of the comment author.")
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Original last-edit time (only together with ``updated_by``).",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="Login or id of the last editor (only together with ``updated_at``).",
    )
