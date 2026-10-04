"""Pydantic v2 models for Yandex Wiki /pages/{id}/comments responses."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import (
    APIModel,
    DisplayNameStr,
    RequestBody,  # pydantic resolves field types via get_type_hints() at runtime
)
from ycli.yandex.wiki.models import ResolveStatus, User


class Comment(APIModel):
    """A wiki page comment (``/pages/{id}/comments`` item).

    The list payload names the text ``body`` and the author ``{display_name: …}``, so ``content``
    reads the ``body`` key (via ``validation_alias``; it still renders as ``content``) and
    ``author`` flattens ``display_name``.

    ``id`` and ``parent_id`` carry the thread wiring: the list returns a reply *flat* — as a
    sibling of its parent, tagged only by ``parent_id`` (``thread_id`` / ``thread_info`` come back
    ``null``). ``CommentsClient.thread`` reads that wiring to reconstruct a single thread — the
    target comment followed by its descendants — from an otherwise flat listing.

    Examples:
        >>> Comment.model_validate({"author": {"display_name": "Сава"}, "body": "ok"}).content
        'ok'
    """

    id: int | None = Field(default=None, description="Numeric id of the comment.")
    parent_id: int | None = Field(
        default=None, description="Id of the comment this one replies to; ``None`` on a root."
    )
    created_at: str | None = Field(default=None, description="ISO-8601 creation timestamp.")
    author: DisplayNameStr = Field(default=None, description="Name to show for the author.")
    content: str | None = Field(
        default=None, validation_alias="body", description="Text of the comment."
    )


class CommentCreate(RequestBody):
    """Typed body for ``POST /pages/{id}/comments`` — a new comment (or threaded reply).

    ``body`` is the comment text; the rest place it: ``inline_text`` pins it to a quoted
    fragment of the page, ``parent_id`` makes it a reply to another comment, ``thread_id``
    files it into an existing thread.

    Examples:
        >>> CommentCreate(body="LGTM", parent_id=7).model_dump(exclude_none=True)
        {'body': 'LGTM', 'parent_id': 7}
    """

    body: str = Field(description="The comment text (non-empty).")
    inline_text: str | None = Field(
        default=None, description="Page fragment this comment is pinned to (inline comment)."
    )
    parent_id: int | None = Field(
        default=None, description="Id of the comment this one replies to (threaded reply)."
    )
    thread_id: int | None = Field(
        default=None, description="Id of an existing thread to file this comment into."
    )


class CommentReaction(APIModel):
    """One reaction left on a comment (``reactions`` item).

    Examples:
        >>> CommentReaction.model_validate({"type": "like"}).type
        'like'
    """

    type: str | None = Field(
        default=None, description="Kind of reaction, e.g. ``like``, ``heart``, ``check``."
    )
    author: User | None = Field(default=None, description="Who left the reaction.")
    created_at: str | None = Field(default=None, description="ISO-8601 time it was left.")


class CommentCreated(APIModel):
    """The comment returned by ``POST /pages/{id}/comments`` — id + echoed placement fields.

    Examples:
        >>> CommentCreated.model_validate({"id": 5, "body": "LGTM"}).id
        5
    """

    id: int | None = Field(default=None, description="Numeric id of the created comment.")
    body: str | None = Field(default=None, description="The stored comment text.")
    inline_text: str | None = Field(
        default=None, description="Page fragment the comment is pinned to, if inline."
    )
    parent_id: int | None = Field(
        default=None, description="Id of the parent comment, if this is a reply."
    )
    thread_id: int | None = Field(
        default=None, description="Id of the thread the comment belongs to."
    )
    created_at: str | None = Field(default=None, description="ISO-8601 creation timestamp.")
    author: User | None = Field(default=None, description="Who wrote the comment.")
    is_deleted: bool | None = Field(default=None, description="Whether the comment is deleted.")
    resolve_status: ResolveStatus | None = Field(
        default=None, description="``resolved`` or ``unresolved``."
    )
    reactions: list[CommentReaction] = Field(
        default_factory=list, description="Reactions left on the comment."
    )


class CommentDeleteResult(APIModel):
    """Result of ``DELETE /pages/{id}/comments/{comment_id}`` — the page's remaining comment count.

    Examples:
        >>> CommentDeleteResult.model_validate({"comments_count": 4}).comments_count
        4
    """

    comments_count: int = Field(
        description="Number of comments left on the page after this deletion."
    )
