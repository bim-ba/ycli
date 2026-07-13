"""Pydantic v2 models for Yandex Wiki /pages responses (extra='ignore')."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class PageAttributes(APIModel):
    """Optional page metadata (``fields=attributes``) — timestamps, draft flag.

    Example:
        >>> PageAttributes.model_validate({"is_draft": True, "comments_count": 3}).comments_count
        3
    """

    created_at: str | None = None
    modified_at: str | None = None
    comments_count: int | None = None
    is_draft: bool | None = None


class _OwnerUser(APIModel):
    username: str | None = None


class _Owner(APIModel):
    user: _OwnerUser | None = None


class PageDetails(APIModel):
    """A single wiki page (``GET /pages?slug=``) — id, slug, title, optional content.

    ``owner_username`` walks ``owner.user.username`` defensively.

    Example:
        >>> PageDetails.model_validate(
        ...     {"id": 42, "slug": "data/x", "title": "X", "owner": {"user": {"username": "ivan"}}}
        ... ).owner_username
        'ivan'
    """

    id: int
    slug: str
    title: str
    page_type: str | None = None
    content: str | None = None
    owner: _Owner | None = None
    attributes: PageAttributes | None = None

    @property
    def owner_username(self) -> str | None:
        return self.owner.user.username if self.owner and self.owner.user else None


class PageRef(APIModel):
    """A lightweight ``{id, slug}`` reference (``/pages/descendants`` item).

    Example:
        >>> PageRef.model_validate({"id": 1, "slug": "data/a"}).slug
        'data/a'
    """

    id: int
    slug: str


class DescendantsResponse(APIModel):
    """``/pages/descendants`` — a paginated listing of ``{id, slug}`` refs.

    ``next_cursor`` is ``null`` (not absent / not empty string) when the listing is
    exhausted; a caller paginating passes the previous response's ``next_cursor`` back
    as the next request's ``cursor``.

    Example:
        >>> r = DescendantsResponse.model_validate(
        ...     {"results": [{"id": 1, "slug": "data/a"}], "next_cursor": None}
        ... )
        >>> r.results[0].slug, r.next_cursor
        ('data/a', None)
    """

    results: list[PageRef] = Field(default_factory=list)
    next_cursor: str | None = None


class PageRefList(RootModel[list[PageRef]]):
    """A drained, flat list of descendant page refs (no cursor — pagination is internal).

    Example:
        >>> PageRefList([PageRef(id=1, slug="data/a")]).root[0].slug
        'data/a'
    """


class GridRef(APIModel):
    """A dynamic-table (grid) reference attached to a page (``/pages/{id}/grids`` item).

    Grids are identified by a UUID string ``id`` (unlike pages, which use an integer id).

    Example:
        >>> GridRef.model_validate({"id": "abc-uuid", "title": "Roadmap"}).title
        'Roadmap'
    """

    id: str = Field(description="The grid's permanent UUID4 identifier.")
    title: str | None = Field(default=None, description="Human-readable grid title.")
    created_at: str | None = Field(
        default=None, description="ISO-8601 timestamp of when the grid was created."
    )


class GridsResponse(APIModel):
    """Envelope for ``GET /pages/{id}/grids`` — ``{results, next_cursor}``.

    Internal per-page parse type used by ``PagesClient._grids_page``. ``next_cursor`` is
    ``null`` (not absent / not empty string) once the listing is exhausted; a paginating caller
    feeds the previous response's ``next_cursor`` back as the next request's ``cursor``.

    Example:
        >>> GridsResponse.model_validate({"results": [{"id": "g1", "title": "T"}]}).results[0].title
        'T'
    """

    results: list[GridRef] = Field(
        default_factory=list, description="Grid references on this page of the listing."
    )
    next_cursor: str | None = Field(
        default=None,
        description="Cursor for the next page; ``null`` when the listing is exhausted.",
    )


class GridRefList(RootModel[list[GridRef]]):
    """A drained, flat list of grid refs (no cursor — pagination is internal).

    Public return type of ``PagesClient.grids``.

    Example:
        >>> GridRefList([GridRef(id="g1", title="T")]).root[0].id
        'g1'
    """

    root: list[GridRef] = Field(default_factory=list)


class PageDeleteResult(APIModel):
    """Result of ``DELETE /pages/{id}`` — carries the ``recovery_token`` for undo.

    Keep this token: it is the only way to restore the just-deleted page (feed it to
    ``wiki recovery restore`` → ``POST /recovery_tokens/{token}/recover``).

    Example:
        >>> PageDeleteResult.model_validate({"recovery_token": "abc-uuid4"}).recovery_token
        'abc-uuid4'
    """

    recovery_token: str = Field(
        description="UUID4 token restoring the deleted page via /recovery_tokens/{token}/recover."
    )


class PageAppendContentBody(APIModel):
    """Where in the whole page body to append — ``top`` or ``bottom`` (``append-content`` ``body``).

    Example:
        >>> PageAppendContentBody(location="bottom").location
        'bottom'
    """

    location: Literal["top", "bottom"] | None = Field(
        default=None,
        description="Anchor the appended content at the ``top`` or ``bottom`` of the page body.",
    )


class PageAppendContentSection(APIModel):
    """Append relative to a numbered section (``append-content`` ``section``).

    Example:
        >>> PageAppendContentSection(id=3, location="top").id
        3
    """

    id: int | None = Field(default=None, description="Target section id to append relative to.")
    location: Literal["top", "bottom"] | None = Field(
        default=None,
        description="Place the content at the ``top`` or ``bottom`` of that section.",
    )


class PageAppendContentAnchor(APIModel):
    """Append relative to a named text anchor (``append-content`` ``anchor``).

    Example:
        >>> PageAppendContentAnchor(name="Roadmap", regex=True).regex
        True
    """

    name: str | None = Field(default=None, description="Anchor text to append next to.")
    fallback: bool = Field(
        default=False, description="Fall back to the body end if the anchor is not found."
    )
    regex: bool = Field(default=False, description="Treat ``name`` as a regular expression.")


class PageAppendContent(APIModel):
    """Typed body for ``POST /pages/{id}/append-content`` — add YFM without a full rewrite.

    ``content`` is the required, non-empty YFM fragment to append; ``body``, ``section`` and
    ``anchor`` pinpoint where. The live API requires **exactly one** of the three placement
    selectors — a bare ``{content}`` (or two selectors at once) is rejected with a 400
    "mutually exclusive" validation error. Contrast with ``PagesClient.update``, which
    replaces the whole page body.

    Example:
        >>> PageAppendContent(
        ...     content="## More", body=PageAppendContentBody(location="bottom")
        ... ).model_dump(exclude_none=True)
        {'content': '## More', 'body': {'location': 'bottom'}}
    """

    content: str = Field(min_length=1, description="YFM fragment to append (non-empty).")
    body: PageAppendContentBody | None = Field(
        default=None, description="Append at the top/bottom of the whole page body."
    )
    section: PageAppendContentSection | None = Field(
        default=None, description="Append relative to a numbered section."
    )
    anchor: PageAppendContentAnchor | None = Field(
        default=None, description="Append relative to a named text anchor."
    )


class PageClone(APIModel):
    """Typed body for ``POST /pages/{id}/clone`` — copy a page to a new address (async).

    ``target`` is the destination slug; ``subscribe_me`` subscribes the caller to the copy.
    Clone is deferred — see :class:`PageCloneOperation` and poll via the ``operations`` resource.

    Example:
        >>> PageClone(target="data/y", subscribe_me=True).model_dump(exclude_none=True)
        {'target': 'data/y', 'subscribe_me': True}
    """

    target: str = Field(description="Slug of the page's new address after the copy.")
    title: str | None = Field(
        default=None, min_length=1, max_length=255, description="Title of the copy, if renaming."
    )
    subscribe_me: bool = Field(
        default=False, description="Subscribe the caller to changes on the copy."
    )


class PageCloneOperationIdentity(APIModel):
    """Reference to the deferred clone operation (``{type, id}``) inside a clone reply.

    Example:
        >>> PageCloneOperationIdentity(type="clone", id="task-1").id
        'task-1'
    """

    type: Literal["clone", "clone_inline_grid"] | None = Field(
        default=None, description="Operation kind — ``clone`` for a page clone."
    )
    id: str | None = Field(
        default=None, description="Task id to poll via ``operations clone <id>``."
    )


class PageCloneOperation(APIModel):
    """Reply of ``POST /pages/{id}/clone`` — a deferred operation reference to poll.

    Page clone is asynchronous: this returns the ``operation`` and a ``status_url``; poll
    ``operations clone <operation.id>`` until it reaches a terminal state.

    Example:
        >>> PageCloneOperation.model_validate(
        ...     {"operation": {"type": "clone", "id": "task-1"}, "status_url": "u"}
        ... ).operation.id
        'task-1'
    """

    operation: PageCloneOperationIdentity | None = Field(
        default=None, description="The started operation (``id`` is the task to poll)."
    )
    status_url: str | None = Field(
        default=None, description="URL that reports the operation's progress."
    )
    dry_run: bool | None = Field(
        default=None, description="Whether this was a validation-only dry run."
    )
