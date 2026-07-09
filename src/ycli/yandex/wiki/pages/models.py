"""Pydantic v2 models for Yandex Wiki /pages responses (extra='ignore')."""

from __future__ import annotations

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
