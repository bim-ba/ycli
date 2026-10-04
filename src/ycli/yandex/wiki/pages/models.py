"""Pydantic v2 models for Yandex Wiki /pages responses."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.wiki.access.models import PageAccessLists, PageAccessPolicy, PageOwner
from ycli.yandex.wiki.models import (
    Location,
    OrderPosition,
    PageAccessType,
    PageIdentity,
    User,
    UserIdentity,
)

#: What a listing of a page's grids can be sorted by.
GridOrder = Literal["title", "created_at"] | str

#: The kind of a Wiki page.
PageType = Literal["page", "grid", "cloud_page", "wysiwyg", "template"] | str


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


class PageRef(APIModel):
    """A lightweight ``{id, slug}`` reference (``/pages/descendants`` item).

    Examples:
        >>> PageRef.model_validate({"id": 1, "slug": "data/a"}).slug
        'data/a'
    """

    id: int
    slug: str


class PageSummary(PageRef):
    """A page named inside another page's reply: its reference, title and kind.

    Examples:
        >>> PageSummary.model_validate({"id": 1, "slug": "data/a", "title": "A"}).title
        'A'
    """

    title: str | None = Field(default=None, description="Title of the page.")
    page_type: PageType | None = Field(
        default=None, description="Kind of page: page, grid, cloud_page, wysiwyg or template."
    )


class Breadcrumb(APIModel):
    """One step of the path from the root to a page (``breadcrumbs`` item).

    Examples:
        >>> Breadcrumb.model_validate({"title": "Team", "slug": "team", "page_exists": True}).slug
        'team'
    """

    id: int | None = Field(default=None, description="Numeric id of the page at this step.")
    title: str | None = Field(default=None, description="Title of the page at this step.")
    slug: str | None = Field(default=None, description="Slug of the page at this step.")
    page_exists: bool | None = Field(
        default=None, description="Whether a page exists at this slug (a gap in the tree if not)."
    )


class PageRedirect(APIModel):
    """Where a page redirects to (``fields=redirect``).

    Examples:
        >>> PageRedirect.model_validate({"page_id": 9}).page_id
        9
    """

    page_id: int | None = Field(default=None, description="Id of the page this one redirects to.")
    redirect_target: PageSummary | None = Field(
        default=None, description="The page at the end of the redirect chain."
    )


class PageActuality(APIModel):
    """Whether a page is marked up to date or obsolete (``fields=actuality``).

    Examples:
        >>> PageActuality.model_validate({"status": "obsolete", "comment": "moved"}).status
        'obsolete'
    """

    status: Literal["possibly_obsolete", "unspecified", "actual", "obsolete"] | str | None = Field(
        default=None,
        description="``actual``, ``obsolete``, ``possibly_obsolete``, ``unspecified``.",
    )
    marked_at: str | None = Field(default=None, description="ISO-8601 time the mark was set.")
    user: User | None = Field(default=None, description="Who set the mark.")
    comment: str | None = Field(default=None, description="Note left with the mark.")
    external_links: list[str] | None = Field(
        default=None, description="Links to the up-to-date material outside the wiki."
    )
    actual_pages: list[PageSummary] | None = Field(
        default=None, description="Wiki pages that replace an obsolete one."
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

    status: Literal["pending_publication", "published"] | str | None = Field(
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
    page_type: PageType | None = Field(
        default=None, description="Kind of page: page, grid, cloud_page, wysiwyg or template."
    )
    revision_draft: RevisionDraft | None = Field(
        default=None, description="Draft the revision was published from, if any."
    )
    publication: RevisionPublication | None = Field(
        default=None, description="Whether the revision is published yet."
    )


class PageDetails(APIModel):
    """A single wiki page (``GET /pages?slug=``) — id, slug, title, optional content.

    ``content``, ``attributes``, ``owner``, ``access_policy``, ``access_lists``, ``breadcrumbs``,
    ``redirect`` and ``actuality`` come back only when named in ``fields``; ``active_revision``
    only when the page was asked for at a past revision. ``owner_username`` walks
    ``owner.user.username`` defensively.

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
    breadcrumbs: list[Breadcrumb] | None = Field(
        default=None, description="Path from the root to the page (``fields=breadcrumbs``)."
    )
    redirect: PageRedirect | None = Field(
        default=None,
        description="Where the page redirects to (``fields=redirect``); ``null`` if nowhere.",
    )
    actuality: PageActuality | None = Field(
        default=None, description="Up-to-date or obsolete mark (``fields=actuality``)."
    )
    active_revision: PageRevision | None = Field(
        default=None,
        description="The past revision shown, when the page was asked for with ``revision_id``.",
    )

    @property
    def owner_username(self) -> str | None:
        """The owner's username, or ``None`` when the page has no owner or the owner no user."""
        return self.owner.user.username if self.owner and self.owner.user else None


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


class PageAccessPolicyUpdate(RequestBody):
    """Who may open a page, in a create or update body (``access_policy``).

    Examples:
        >>> PageAccessPolicyUpdate(access_type="all_staff", all_staff_role="editor").access_type
        'all_staff'
    """

    access_type: PageAccessType = Field(
        description="``inherited`` (as the parent), ``all_staff`` or ``custom``."
    )
    all_staff_role: str | None = Field(
        default=None, description="Role every employee gets under ``all_staff``, e.g. editor."
    )


class PageRedirectUpdate(RequestBody):
    """Where a page should redirect to (``redirect`` of an update body).

    ``page`` has no default: ``None`` is sent as ``null`` and removes the redirect.

    Examples:
        >>> PageRedirectUpdate(page=PageIdentity(slug="eng/new")).page.slug
        'eng/new'
    """

    page: PageIdentity | None = Field(
        description="The page to redirect to, by id or slug; ``None`` removes the redirect."
    )


class PageActualityUpdate(RequestBody):
    """Whether a page is up to date (``actuality`` of an update body).

    Examples:
        >>> PageActualityUpdate(is_actual=False, comment="replaced").is_actual
        False
    """

    is_actual: bool = Field(description="``True`` marks the page up to date, ``False`` obsolete.")
    comment: str | None = Field(default=None, description="Note left with the mark.")
    links: list[str] | None = Field(default=None, description="Links to the up-to-date material.")


class PageOwnerUpdate(RequestBody):
    """The new owner of a page (``owner`` of an update body).

    Examples:
        >>> PageOwnerUpdate(user=UserIdentity(uid="1000")).user.uid
        '1000'
    """

    user: UserIdentity | None = Field(default=None, description="The user who becomes the owner.")


class PageCreate(RequestBody):
    """Typed request body for ``POST /pages``: a new page at ``slug``.

    Examples:
        >>> PageCreate(slug="eng/new", title="New page", content="# New").slug
        'eng/new'
    """

    slug: str = Field(description="Address of the page, e.g. ``data/x``.")
    title: str = Field(min_length=1, max_length=255, description="Title of the page.")
    content: str | None = Field(default=None, description="Body of the page in YFM markdown.")
    access_policy: PageAccessPolicyUpdate | None = Field(
        default=None, description="Who may open the page."
    )


class PageUpdate(RequestBody):
    """Typed request body for ``POST /pages/{id}``: only the fields set are changed.

    A page's address is not among them: :class:`PageMove` renames or relocates a page.

    Examples:
        >>> PageUpdate(content="# Rewritten", title="Renamed").title
        'Renamed'
    """

    title: str | None = Field(
        default=None, min_length=1, max_length=255, description="New title of the page."
    )
    content: str | None = Field(default=None, description="New body, replacing the whole one.")
    redirect: PageRedirectUpdate | None = Field(
        default=None, description="Make the page a redirect, or remove its redirect."
    )
    actuality: PageActualityUpdate | None = Field(
        default=None, description="Mark the page up to date or obsolete."
    )
    access_policy: PageAccessPolicyUpdate | None = Field(
        default=None, description="Who may open the page."
    )
    owner: PageOwnerUpdate | None = Field(default=None, description="The new owner of the page.")


class PageAppendContentBody(RequestBody):
    """Where in the whole page body to append — ``top`` or ``bottom`` (``append-content`` ``body``).

    Examples:
        >>> PageAppendContentBody(location="bottom").location
        'bottom'
    """

    location: Location | None = Field(
        default=None,
        description="Anchor the appended content at the ``top`` or ``bottom`` of the page body.",
    )


class PageAppendContentSection(RequestBody):
    """Append relative to a numbered section (``append-content`` ``section``).

    Examples:
        >>> PageAppendContentSection(id=3, location="top").id
        3
    """

    id: int | None = Field(default=None, description="Target section id to append relative to.")
    location: Location | None = Field(
        default=None,
        description="Place the content at the ``top`` or ``bottom`` of that section.",
    )


class PageAppendContentAnchor(RequestBody):
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


class PageAppendContent(RequestBody):
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


class PageClone(RequestBody):
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


class PageMoveStep(RequestBody):
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
    position: OrderPosition | None = Field(
        default=None, description="Put the moved page ``before`` or ``after`` ``next_to_slug``."
    )


class PageMove(RequestBody):
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
