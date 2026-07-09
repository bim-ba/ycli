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
    """Envelope for ``GET /pages/{id}/comments`` — ``{results, next_cursor}``.

    Internal per-page parse type used by ``CommentsClient._list_page``. ``next_cursor`` is
    ``null`` (not absent / not empty string) once the listing is exhausted; a paginating caller
    feeds the previous response's ``next_cursor`` back as the next request's ``cursor``.

    Example:
        >>> CommentsResponse.model_validate({"results": [{"content": "ok"}]}).results[0].content
        'ok'
    """

    results: list[Comment] = Field(default_factory=list)
    next_cursor: str | None = Field(
        default=None,
        description="Cursor for the next page; ``null`` when the listing is exhausted.",
    )


class CommentList(RootModel[list[Comment]]):
    """Flat collection of :class:`Comment` items — public return type of ``CommentsClient.list``.

    Example:
        >>> CommentList([Comment.model_validate({"content": "ok"})]).root[0].content
        'ok'
    """

    root: list[Comment] = Field(default_factory=list)


class CommentCreate(APIModel):
    """Typed body for ``POST /pages/{id}/comments`` — a new comment (or threaded reply).

    ``body`` is the comment text; the rest place it: ``inline_text`` pins it to a quoted
    fragment of the page, ``parent_id`` makes it a reply to another comment, ``thread_id``
    files it into an existing thread.

    Example:
        >>> CommentCreate(body="LGTM", parent_id=7).model_dump(exclude_none=True)
        {'body': 'LGTM', 'parent_id': 7}
    """

    body: str = Field(min_length=1, description="The comment text (non-empty).")
    inline_text: str | None = Field(
        default=None, description="Page fragment this comment is pinned to (inline comment)."
    )
    parent_id: int | None = Field(
        default=None, description="Id of the comment this one replies to (threaded reply)."
    )
    thread_id: int | None = Field(
        default=None, description="Id of an existing thread to file this comment into."
    )


class CommentCreated(APIModel):
    """The comment returned by ``POST /pages/{id}/comments`` — id + echoed placement fields.

    Example:
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


class CommentDeleteResult(APIModel):
    """Result of ``DELETE /pages/{id}/comments/{comment_id}`` — the page's remaining comment count.

    Example:
        >>> CommentDeleteResult.model_validate({"comments_count": 4}).comments_count
        4
    """

    comments_count: int = Field(
        description="Number of comments left on the page after this deletion."
    )
