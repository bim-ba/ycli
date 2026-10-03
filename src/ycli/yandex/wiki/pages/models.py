"""Pydantic v2 models for Yandex Wiki /pages responses (extra='ignore')."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel
from ycli.yandex.wiki.access.models import PageAccessLists, PageAccessPolicy, PageOwner
from ycli.yandex.wiki.models import AsyncOperation, OperationIdentity, User


class PageAttributes(APIModel):
    """Optional page metadata (``fields=attributes``) — timestamps, draft flag.

    Examples:
        >>> PageAttributes.model_validate({"is_draft": True, "comments_count": 3}).comments_count
        3
    """

    created_at: str | None = None
    modified_at: str | None = None
    comments_count: int | None = None
    is_draft: bool | None = None


class PageDetails(APIModel):
    """A single wiki page (``GET /pages?slug=``) — id, slug, title, optional content.

    ``content``, ``attributes``, ``owner``, ``access_policy`` and ``access_lists`` come back only
    when named in ``fields``. ``owner_username`` walks ``owner.user.username`` defensively.

    Examples:
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
    owner: PageOwner | None = Field(default=None, description="Owner (``fields=owner``).")
    attributes: PageAttributes | None = None
    access_policy: PageAccessPolicy | None = Field(
        default=None, description="Who may open the page (``fields=access_policy``)."
    )
    access_lists: PageAccessLists | None = Field(
        default=None,
        description="Personal accesses: direct, by link, inherited (``fields=access_lists``).",
    )

    @property
    def owner_username(self) -> str | None:
        """The owner's username, or ``None`` when the page has no owner or the owner no user."""
        return self.owner.user.username if self.owner and self.owner.user else None


class PageRef(APIModel):
    """A lightweight ``{id, slug}`` reference (``/pages/descendants`` item).

    Examples:
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

    Examples:
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

    Examples:
        >>> PageRefList([PageRef(id=1, slug="data/a")]).root[0].slug
        'data/a'
    """


class GridRef(APIModel):
    """A dynamic-table (grid) reference attached to a page (``/pages/{id}/grids`` item).

    Grids are identified by a UUID string ``id`` (unlike pages, which use an integer id).

    Examples:
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

    Internal per-page parse type used by ``endpoints.list_grids``. ``next_cursor`` is
    ``null`` (not absent / not empty string) once the listing is exhausted; a paginating caller
    feeds the previous response's ``next_cursor`` back as the next request's ``cursor``.

    Examples:
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

    Examples:
        >>> GridRefList([GridRef(id="g1", title="T")]).root[0].id
        'g1'
    """

    root: list[GridRef] = Field(default_factory=list)


class PageDeleteResult(APIModel):
    """Result of ``DELETE /pages/{id}`` — carries the ``recovery_token`` for undo.

    Keep this token: it is the only way to restore the just-deleted page (feed it to
    ``wiki recovery restore`` → ``POST /recovery_tokens/{token}/recover``).

    Examples:
        >>> PageDeleteResult.model_validate({"recovery_token": "abc-uuid4"}).recovery_token
        'abc-uuid4'
    """

    recovery_token: str = Field(
        description="UUID4 token restoring the deleted page via /recovery_tokens/{token}/recover."
    )


class PageAppendContentBody(APIModel):
    """Where in the whole page body to append — ``top`` or ``bottom`` (``append-content`` ``body``).

    Examples:
        >>> PageAppendContentBody(location="bottom").location
        'bottom'
    """

    location: Literal["top", "bottom"] | None = Field(
        default=None,
        description="Anchor the appended content at the ``top`` or ``bottom`` of the page body.",
    )


class PageAppendContentSection(APIModel):
    """Append relative to a numbered section (``append-content`` ``section``).

    Examples:
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

    Examples:
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

    Examples:
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
    Clone is deferred — see :class:`AsyncOperation` and poll via the ``operations`` resource.

    Examples:
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


class PageMoveStep(APIModel):
    """One step of a page move: take the page at ``source`` and give it the address ``target``.

    ``next_to_slug`` and ``position`` set where the moved page lands among its new siblings.

    Examples:
        >>> PageMoveStep(source="data/old", target="archive/old").model_dump(exclude_none=True)
        {'source': 'data/old', 'target': 'archive/old'}
    """

    source: str = Field(description="Slug of the page before the move.")
    target: str = Field(description="Slug of the page after the move.")
    next_to_slug: str | None = Field(
        default=None, description="Sibling page to place the moved page next to."
    )
    position: Literal["before", "after"] | None = Field(
        default=None, description="Put the moved page ``before`` or ``after`` ``next_to_slug``."
    )


class PageMove(APIModel):
    """Typed body for ``POST /pages/move`` — give pages new addresses (async, undocumented).

    The API runs the steps in order. It moves a page together with its subtree, which is the only
    way to rename or relocate a page (a page update has no ``slug``). The endpoint is undocumented
    by Yandex (live OpenAPI only) and may change.

    Examples:
        >>> PageMove(
        ...     operations=[PageMoveStep(source="data/old", target="archive/old")],
        ...     copy_inherited_access=True,
        ... ).model_dump(exclude_none=True)["copy_inherited_access"]
        True
    """

    operations: list[PageMoveStep] = Field(
        min_length=1, description="Moves to run, in order (at least one)."
    )
    copy_inherited_access: bool = Field(
        default=False,
        description="Copy the accesses a page inherited from its old parent when it moves. The "
        "API refuses a move that leaves this unset (400 INHERITANCE_BEHAVIOR_IS_NOT_SPECIFIED), "
        "so it is always sent, ``false`` by default.",
    )


class RevisionDraft(APIModel):
    """The draft a revision was published from (``revision_draft`` of a revision).

    Examples:
        >>> RevisionDraft.model_validate({"id": 3, "modified_at": "2026-10-03T10:00:00Z"}).id
        3
    """

    id: int | None = Field(default=None, description="Draft id.")
    created_at: str | None = Field(default=None, description="ISO-8601 time the draft was made.")
    modified_at: str | None = Field(default=None, description="ISO-8601 time of its last edit.")


class RevisionPublication(APIModel):
    """Publication state of a revision (``publication`` of a revision).

    Examples:
        >>> RevisionPublication(status="published").status
        'published'
    """

    status: Literal["pending_publication", "published"] | None = Field(
        default=None, description="``pending_publication`` or ``published``."
    )


class PageRevision(APIModel):
    """One saved revision of a page (``/pages/{id}/revisions`` item).

    Examples:
        >>> PageRevision.model_validate(
        ...     {"id": 7, "author": {"username": "ivan"}, "page_type": "page"}
        ... ).author.username
        'ivan'
    """

    id: int = Field(description="Revision id (the ``revision_id`` of ``GET /pages``).")
    author: User | None = Field(default=None, description="Who saved the revision.")
    created_at: str | None = Field(default=None, description="ISO-8601 time it was saved.")
    page_type: str | None = Field(
        default=None, description="Kind of page: page, grid, cloud_page, wysiwyg or template."
    )
    revision_draft: RevisionDraft | None = Field(
        default=None, description="Draft the revision was published from, if any."
    )
    publication: RevisionPublication | None = Field(
        default=None, description="Whether the revision is published yet."
    )


class RevisionsResponse(APIModel):
    """Envelope for ``GET /pages/{id}/revisions`` — ``{results, next_cursor}``.

    Internal per-page parse type used by ``endpoints.list_revisions``.

    Examples:
        >>> RevisionsResponse.model_validate({"results": [{"id": 7}]}).results[0].id
        7
    """

    results: list[PageRevision] = Field(
        default_factory=list, description="Revisions on this page of the listing."
    )
    next_cursor: str | None = Field(
        default=None,
        description="Cursor for the next page; ``null`` when the listing is exhausted.",
    )


class PageRevisionList(RootModel[list[PageRevision]]):
    """A drained, flat list of page revisions (no cursor — pagination is internal).

    Examples:
        >>> PageRevisionList([PageRevision(id=7)]).root[0].id
        7
    """

    root: list[PageRevision] = Field(default_factory=list)


class BacklinksResponse(APIModel):
    """Envelope for ``GET /pages/{id}/backlinks`` — ``{results, next_cursor}`` of page refs.

    Internal per-page parse type used by ``endpoints.list_backlinks``.

    Examples:
        >>> BacklinksResponse.model_validate({"results": [{"id": 1, "slug": "a"}]}).results[0].slug
        'a'
    """

    results: list[PageRef] = Field(
        default_factory=list, description="Pages that link here, on this page of the listing."
    )
    next_cursor: str | None = Field(
        default=None,
        description="Cursor for the next page; ``null`` when the listing is exhausted.",
    )


PageCloneOperation = AsyncOperation  # deprecated, removed in 0.38
PageCloneOperationIdentity = OperationIdentity  # deprecated, removed in 0.38
PageMoveOperation = AsyncOperation  # deprecated, removed in 0.38
