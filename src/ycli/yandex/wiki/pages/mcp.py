"""Wiki /pages FastMCP tools — pure, DI via Depends, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Listed, SortDirection
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    All,
    Next,
    Slug,
    app_config,
    new_server,
    wiki_client,
)
from ycli.yandex.wiki.models import AsyncOperation
from ycli.yandex.wiki.pages.models import (
    GridOrder,
    GridRef,
    PageAppendContent,
    PageClone,
    PageCreate,
    PageDeleteResult,
    PageDetails,
    PageMove,
    PageRef,
    PageRevision,
    PageUpdate,
    SearchPage,
    SearchRequest,
)

mcp = new_server("wiki-pages")

RevisionID = Annotated[
    int | None,
    Field(description="Show this past revision (an id from ``pages_revisions_list``)."),
]
RaiseOnRedirect = Annotated[
    bool | None, Field(description="Fail if the page is a redirect instead of following it.")
]
PageReplyFields = Annotated[
    str | None,
    Field(description="Extra blocks to include in the reply (CSV), e.g. ``content,attributes``."),
]
Silent = Annotated[bool | None, Field(description="Do not notify the page's subscribers.")]
IncludeSelf = Annotated[bool | None, Field(description="Also return the ancestor page itself.")]
ShowAll = Annotated[bool | None, Field(description="The API's ``show_all`` flag.")]
Actuality = Annotated[
    str | None, Field(description="Only the pages in this state: `actual` or `obsolete`.")
]
OrderDirection = Annotated[
    SortDirection | None, Field(description="Sort direction for ``order_by``.")
]


@mcp.tool(name="pages_get", annotations={**RO, "title": "Get Wiki page"})
def get(
    slug: Slug,
    revision_id: RevisionID = None,
    raise_on_redirect: RaiseOnRedirect = None,
    client: WikiClient = Depends(wiki_client),
) -> str:
    """The page's markdown body for SLUG."""
    # violation(as-given): the API returns a page without its text unless asked; `get` shows it
    page = client.pages.get(
        slug=slug, fields="content", revision_id=revision_id, raise_on_redirect=raise_on_redirect
    )
    return page.content or ""


@mcp.tool(name="pages_get_meta", annotations={**RO, "title": "Get Wiki page metadata"})
def get_meta(slug: Slug, client: WikiClient = Depends(wiki_client)) -> PageDetails:
    """Page metadata for SLUG (attributes + owner)."""
    # violation(as-given): the API returns neither block unless asked; `get-meta` is those two
    return client.pages.get(slug=slug, fields="attributes,owner")


@mcp.tool(name="pages_descendants_list", annotations={**RO, "title": "List Wiki page descendants"})
def descendants_list(
    slug: Slug,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max descendant refs to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    include_self: IncludeSelf = None,
    show_all: ShowAll = None,
    actuality: Actuality = None,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> Listed[PageRef]:
    """All descendant refs under SLUG, auto-paginated.

    Capped at the configured item cap unless ``limit`` is given; narrow by SLUG for large trees.
    """
    cap = config.http.cap(limit, all_=all)
    return client.pages.descendants_list(
        slug=slug,
        limit=cap,
        next=next,
        actuality=actuality,
        include_self=include_self,
        show_all=show_all,
    ).collect()


@mcp.tool(name="pages_grids_list", annotations={**RO, "title": "List Wiki page grids"})
def grids_list(
    page_id: Annotated[int, Field(description="Numeric page id whose grids to list.")],
    limit: Annotated[
        int | None, Field(ge=1, description="Max grids (omitted: the configured cap).")
    ] = None,
    all: All = False,
    next: Next = None,
    order_by: Annotated[GridOrder | None, Field(description="Sort field.")] = None,
    order_direction: OrderDirection = None,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> Listed[GridRef]:
    """Dynamic tables (grids) attached to a page id, auto-paginated (drains ``next_cursor``).

    Each grid ref is a UUID ``id`` + ``title`` + ``created_at``. Capped at the configured item cap
    unless ``limit`` is given. Reads a page's numeric id — pair with
    ``pages_get_meta`` / ``pages_descendants_list`` (whose refs carry the ids) to find one.
    """
    cap = config.http.cap(limit, all_=all)
    return client.pages.grids_list(
        page_id=page_id,
        limit=cap,
        next=next,
        order_by=order_by,
        order_direction=order_direction,
    ).collect()


@mcp.tool(name="pages_get_by_id", annotations={**RO, "title": "Get Wiki page by id"})
def get_by_id(
    page_id: Annotated[int, Field(description="Numeric page id to fetch.")],
    fields: Annotated[
        str | None,
        Field(
            description="Extra blocks (CSV), e.g. ``content,attributes,breadcrumbs``. "
            "Omitted = id/slug/title only."
        ),
    ] = None,
    revision_id: RevisionID = None,
    raise_on_redirect: RaiseOnRedirect = None,
    client: WikiClient = Depends(wiki_client),
) -> PageDetails:
    """A single page by its numeric id — the id-based twin of ``pages_get``/``pages_get_meta``.

    Use it when you hold a numeric page id (e.g. from a descendants listing or a write's
    response) instead of the slug. ``fields`` follows the standard Wiki selector rules:
    without it the response carries id/slug/title only; ask for ``content`` or
    ``attributes`` explicitly.
    """
    return client.pages.get_by_id(
        page_id=page_id,
        fields=fields,
        revision_id=revision_id,
        raise_on_redirect=raise_on_redirect,
    )


@mcp.tool(
    name="pages_descendants_list_by_id",
    annotations={**RO, "title": "List Wiki page descendants by id"},
)
def descendants_list_by_id(
    page_id: Annotated[int, Field(description="Numeric page id whose subtree to list.")],
    limit: Annotated[
        int | None, Field(ge=1, description="Max refs (omitted: the configured cap).")
    ] = None,
    all: All = False,
    next: Next = None,
    include_self: IncludeSelf = None,
    show_all: ShowAll = None,
    actuality: Actuality = None,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> Listed[PageRef]:
    """All descendant page refs under a numeric page id, auto-paginated.

    The id-based twin of ``pages_descendants_list``. Capped at the configured item cap
    unless ``limit`` is given; each ref carries the child's numeric ``id`` and permanent
    ``slug``.
    """
    cap = config.http.cap(limit, all_=all)
    return client.pages.descendants_list_by_id(
        page_id=page_id,
        limit=cap,
        next=next,
        actuality=actuality,
        include_self=include_self,
        show_all=show_all,
    ).collect()


@mcp.tool(name="pages_create", annotations={**WRITE, "title": "Create Wiki page"})
def create(
    body: PageCreate,
    fields: PageReplyFields = None,
    is_silent: Silent = None,
    client: WikiClient = Depends(wiki_client),
) -> PageDetails:
    """Create a wiki page at ``body.slug`` (``POST /pages``).

    Treat the slug as permanent: ``pages_move`` can rename the page later, but the old address
    then answers 404 and links to it break, so pick the slug carefully. Returns the created page
    (its numeric ``id`` drives the id-based tools and every subsequent write). E.g.
    ``{"body": {"slug": "data/x", "title": "X", "content": "# X"}}``.
    """
    return client.pages.create(body=body, fields=fields, is_silent=is_silent)


@mcp.tool(
    name="pages_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Wiki page"},
)
def update(
    page_id: Annotated[int, Field(description="Numeric id of the page to update.")],
    body: PageUpdate,
    fields: PageReplyFields = None,
    is_silent: Silent = None,
    allow_merge: Annotated[
        bool | None,
        Field(description="Merge with a concurrent edit (3-way merge) instead of failing."),
    ] = None,
    client: WikiClient = Depends(wiki_client),
) -> PageDetails:
    """Change a wiki page by numeric id: only the fields set in ``body`` change.

    ``body.content`` REPLACES the whole text — to add to an existing page use ``pages_append``
    instead. The Wiki API updates via POST, not PATCH (PATCH returns 405); the SDK already
    handles that quirk. Repeating the same call yields the same page state (idempotent). E.g.
    ``{"page_id": 7, "body": {"title": "New name"}}``.
    """
    return client.pages.update(
        page_id=page_id,
        body=body,
        fields=fields,
        is_silent=is_silent,
        allow_merge=allow_merge,
    )


@mcp.tool(name="pages_delete", annotations={**DESTRUCTIVE, "title": "Delete Wiki page"})
def delete(
    page_id: Annotated[int, Field(description="Numeric id of the page to delete.")],
    recursive: Annotated[bool | None, Field(description="Also delete every page under it.")] = None,
    client: WikiClient = Depends(wiki_client),
) -> PageDeleteResult:
    """Delete a wiki page by numeric id (``DELETE /pages/{id}``).

    KEEP the returned ``recovery_token`` — it is the only handle to undo the delete
    (redeem it with ``recovery_recover``). Deleting removes the page's descendants'
    anchor too, so double-check the id (``pages_get_by_id``) before calling.
    """
    return client.pages.delete(page_id=page_id, recursive=recursive)


@mcp.tool(
    name="pages_append",
    annotations={**WRITE, "title": "Append content to Wiki page"},
)
def append(
    page_id: Annotated[int, Field(description="Numeric id of the page to append to.")],
    body: Annotated[
        PageAppendContent,
        Field(
            description="What to append and where: required ``content`` (YFM fragment) plus "
            "optional ``body`` (top/bottom), ``section`` or ``anchor`` placement."
        ),
    ],
    fields: PageReplyFields = None,
    is_silent: Silent = None,
    client: WikiClient = Depends(wiki_client),
) -> PageDetails:
    """Append a YFM fragment to a wiki page without rewriting the whole body.

    Unlike ``pages_update`` (full replace), this adds ``body.content`` at the chosen spot:
    ``body.body.location`` (top/bottom of the page), a numbered ``body.section``, or a named
    text ``body.anchor``. Returns the updated page.
    """
    return client.pages.append(
        page_id=page_id,
        body=body,
        fields=fields,
        is_silent=is_silent,
    )


@mcp.tool(name="pages_clone", annotations={**WRITE, "title": "Clone Wiki page"})
def clone(
    page_id: Annotated[int, Field(description="Numeric id of the page to copy.")],
    body: Annotated[
        PageClone,
        Field(
            description="Clone spec: required ``target`` (destination slug) plus optional "
            "``title`` and ``subscribe_me``."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> AsyncOperation:
    """Copy a page to a new address (``POST /pages/{id}/clone`` — asynchronous).

    Cloning leaves the original where it is; to give the page itself a new slug use
    ``pages_move``. The call returns a deferred operation reference — poll
    ``operations_clone_get`` with the returned ``operation.id`` until it reaches a terminal status.
    """
    return client.pages.clone(page_id=page_id, body=body)


@mcp.tool(name="pages_move", annotations={**WRITE, "title": "Move Wiki page"})
def move(
    body: Annotated[
        PageMove,
        Field(
            description="Move spec: ``operations`` (each ``source`` slug and new ``target`` slug, "
            "optionally ``next_to_slug`` with ``position`` before/after) and optional "
            "``copy_inherited_access``."
        ),
    ],
    validate_only: Annotated[
        bool | None, Field(description="Validate the move without applying it.")
    ] = None,
    client: WikiClient = Depends(wiki_client),
) -> AsyncOperation:
    """Move or rename pages (``POST /pages/move`` — asynchronous; undocumented by Yandex).

    The only way to give a page a new slug. The call returns a deferred operation reference —
    poll ``operations_move_get`` with the returned ``operation.id`` until it reaches a terminal
    status. A page moves with its subtree and links to the old address may stop working, so try
    ``validate_only=true`` first: it validates the request, applies nothing, and its operation id
    cannot be polled. Yandex does not document this operation (it is in the live OpenAPI only)
    and may change it.
    """
    return client.pages.move(body=body, validate_only=validate_only)


@mcp.tool(
    name="pages_revisions_list",
    annotations={**RO, "title": "List Wiki page revisions"},
)
def revisions_list(
    page_id: Annotated[int, Field(description="Numeric page id whose revisions to list.")],
    ids: Annotated[
        str | None, Field(description="Only these revision ids (comma separated).")
    ] = None,
    limit: Annotated[
        int | None, Field(ge=1, description="Max revisions (omitted: the configured cap).")
    ] = None,
    all: All = False,
    next: Next = None,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> Listed[PageRevision]:
    """Saved revisions of a page, auto-paginated (``GET /pages/{id}/revisions``).

    Each revision has an ``id`` (what ``GET /pages`` takes as ``revision_id``), its ``author``,
    ``created_at``, ``page_type`` and publication state. Yandex does not document this operation
    (it is in the live OpenAPI only) and may change it.
    """
    cap = config.http.cap(limit, all_=all)
    return client.pages.revisions_list(page_id=page_id, ids=ids, limit=cap, next=next).collect()


@mcp.tool(
    name="pages_backlinks_list",
    annotations={**RO, "title": "List Wiki page backlinks"},
)
def backlinks_list(
    page_id: Annotated[int, Field(description="Numeric id of the page that is linked to.")],
    for_cluster: Annotated[
        bool | None, Field(description="Links to the page's whole subtree, not just the page.")
    ] = None,
    show_all: Annotated[
        bool | None,
        Field(description="The API's ``show_all`` flag (undocumented; no effect seen live)."),
    ] = None,
    limit: Annotated[
        int | None, Field(ge=1, description="Max refs (omitted: the configured cap).")
    ] = None,
    all: All = False,
    next: Next = None,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> Listed[PageRef]:
    """Refs (``id`` and ``slug``) of the pages that link to a page (``GET /pages/{id}/backlinks``).

    Auto-paginated. Yandex does not document this operation (it is in the live OpenAPI only) and
    may change it.
    """
    cap = config.http.cap(limit, all_=all)
    return client.pages.backlinks_list(
        page_id=page_id, for_cluster=for_cluster, show_all=show_all, limit=cap, next=next
    ).collect()


@mcp.tool(name="pages_search", annotations={**RO, "title": "Search Wiki"})
def search(body: SearchRequest, client: WikiClient = Depends(wiki_client)) -> SearchPage:
    """Full-text search over wiki pages and files; returns one page of hits.

    Each hit has the page ``slug`` (read it with ``pages_get``), ``title``, a ``content``
    snippet, the ``type`` and ``modified_at``. ``body.filters`` narrows the search by ``type``,
    ``authors``, ``cluster`` (a page slug), ``created_at`` / ``modified_at`` (a window with both
    ``from`` and ``to``) and ``show_obsolete``. For the next page pass ``next_cursor`` back as
    ``body.cursor``; stop at the first page without hits, because ``next_cursor`` stays set
    after an empty page. A new page can take seconds to appear in the index. E.g.
    ``{"body": {"query": "roadmap", "limit": 5}}``.
    """
    return client.pages.search(body)
