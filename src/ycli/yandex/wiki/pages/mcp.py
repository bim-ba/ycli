"""Wiki /pages FastMCP tools — pure, DI via Depends, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    app_config,
    wiki_client,
)
from ycli.yandex.wiki.pages.models import (
    GridRefList,
    PageAppendContent,
    PageClone,
    PageCloneOperation,
    PageDeleteResult,
    PageDetails,
    PageRefList,
)

mcp = FastMCP("wiki-pages")


@mcp.tool(name="pages_get", annotations={**RO, "title": "Get Wiki page"}, tags=TAGS)
def get(slug: str, client: WikiClient = Depends(wiki_client)) -> str:
    """The page's markdown body for SLUG."""
    return client.pages.get(slug=slug, fields="content").content or ""


@mcp.tool(name="pages_meta", annotations={**RO, "title": "Get Wiki page metadata"}, tags=TAGS)
def meta(slug: str, client: WikiClient = Depends(wiki_client)) -> PageDetails:
    """Page metadata for SLUG (attributes + owner)."""
    return client.pages.get(slug=slug, fields="attributes,owner")


@mcp.tool(
    name="pages_descendants", annotations={**RO, "title": "List Wiki page descendants"}, tags=TAGS
)
def descendants(
    slug: str,
    limit: int = 0,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> PageRefList:
    """All descendant refs under SLUG, auto-paginated. Capped at YCLI_MAX_ITEMS (default 500)
    unless ``limit`` is given; narrow by SLUG for large trees."""
    cap = resolve_cap(limit, config.max_items)
    return client.pages.descendants(slug=slug, limit=cap)


@mcp.tool(name="pages_grids_list", annotations={**RO, "title": "List Wiki page grids"}, tags=TAGS)
def grids_list(
    page_id: Annotated[int, Field(description="Numeric page id whose grids to list.")],
    limit: Annotated[int, Field(description="Max grids (0 = YCLI_MAX_ITEMS cap).")] = 0,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> GridRefList:
    """Dynamic tables (grids) attached to a page id, auto-paginated (drains ``next_cursor``).

    Each grid ref is a UUID ``id`` + ``title`` + ``created_at``. Capped at YCLI_MAX_ITEMS
    (default 500) unless ``limit`` is given. Reads a page's numeric id — pair with
    ``pages_meta`` / ``pages_descendants`` (whose refs carry the ids) to find one.

    Example:
        >>> grids_list(page_id=12345, limit=50)  # doctest: +SKIP
    """
    cap = resolve_cap(limit, config.max_items)
    return client.pages.grids(page_id=page_id, limit=cap)


@mcp.tool(name="pages_by_id_get", annotations={**RO, "title": "Get Wiki page by id"}, tags=TAGS)
def by_id_get(
    page_id: Annotated[int, Field(description="Numeric page id to fetch.")],
    fields: Annotated[
        str | None,
        Field(
            description="Extra blocks (CSV), e.g. ``content,attributes,breadcrumbs``. "
            "Omitted = id/slug/title only."
        ),
    ] = None,
    client: WikiClient = Depends(wiki_client),
) -> PageDetails:
    """A single page by its numeric id — the id-based twin of ``pages_get``/``pages_meta``.

    Use it when you hold a numeric page id (e.g. from a descendants listing or a write's
    response) instead of the slug. ``fields`` follows the standard Wiki selector rules:
    without it the response carries id/slug/title only; ask for ``content`` or
    ``attributes`` explicitly.

    Example:
        >>> by_id_get(page_id=12345, fields="content")  # doctest: +SKIP
    """
    return client.pages.get_by_id(page_id=page_id, fields=fields)


@mcp.tool(
    name="pages_by_id_descendants",
    annotations={**RO, "title": "List Wiki page descendants by id"},
    tags=TAGS,
)
def by_id_descendants(
    page_id: Annotated[int, Field(description="Numeric page id whose subtree to list.")],
    limit: Annotated[int, Field(description="Max refs (0 = YCLI_MAX_ITEMS cap).")] = 0,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> PageRefList:
    """All descendant page refs under a numeric page id, auto-paginated.

    The id-based twin of ``pages_descendants``. Capped at YCLI_MAX_ITEMS (default 500)
    unless ``limit`` is given; each ref carries the child's numeric ``id`` and permanent
    ``slug``.

    Example:
        >>> by_id_descendants(page_id=12345, limit=50)  # doctest: +SKIP
    """
    cap = resolve_cap(limit, config.max_items)
    return client.pages.descendants_by_id(page_id=page_id, limit=cap)


@mcp.tool(name="pages_create", annotations={**WRITE, "title": "Create Wiki page"}, tags=WRITE_TAGS)
def create(
    slug: Annotated[
        str, Field(description="Target slug, e.g. ``data/x``. Slugs are PERMANENT once created.")
    ],
    title: Annotated[str, Field(description="Page title.")],
    content: Annotated[str, Field(description="Page body in YFM markdown.")],
    client: WikiClient = Depends(wiki_client),
) -> PageDetails:
    """Create a wiki page at ``slug`` (``POST /pages``).

    Slugs are permanent — a page cannot be renamed to another address later (only cloned),
    so pick the slug carefully. Returns the created page (its numeric ``id`` drives the
    id-based tools and every subsequent write).

    Example:
        >>> create(slug="data/x", title="X", content="# X")  # doctest: +SKIP
    """
    return client.pages.create(body={"slug": slug, "title": title, "content": content})


@mcp.tool(
    name="pages_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Wiki page"},
    tags=WRITE_TAGS,
)
def update(
    page_id: Annotated[int, Field(description="Numeric id of the page to update.")],
    content: Annotated[str, Field(description="New page body in YFM markdown (full replace).")],
    title: Annotated[str | None, Field(description="New title (unchanged when omitted).")] = None,
    client: WikiClient = Depends(wiki_client),
) -> PageDetails:
    """Replace a wiki page's body (and optionally its title) by numeric id.

    This REPLACES the whole body — to add to an existing page use ``pages_append_content``
    instead. The Wiki API updates via POST, not PATCH (PATCH returns 405); the SDK already
    handles that quirk. Repeating the same call yields the same page state (idempotent).

    Example:
        >>> update(page_id=12345, content="# Updated")  # doctest: +SKIP
    """
    body: dict[str, str] = {"content": content}
    if title is not None:
        body["title"] = title
    return client.pages.update(page_id=page_id, body=body)


@mcp.tool(
    name="pages_delete", annotations={**DESTRUCTIVE, "title": "Delete Wiki page"}, tags=WRITE_TAGS
)
def delete(
    page_id: Annotated[int, Field(description="Numeric id of the page to delete.")],
    client: WikiClient = Depends(wiki_client),
) -> PageDeleteResult:
    """Delete a wiki page by numeric id (``DELETE /pages/{id}``).

    KEEP the returned ``recovery_token`` — it is the only handle to undo the delete
    (redeem it with ``recovery_restore``). Deleting removes the page's descendants'
    anchor too, so double-check the id (``pages_by_id_get``) before calling.

    Example:
        >>> delete(page_id=12345)  # doctest: +SKIP
    """
    return client.pages.delete(page_id=page_id)


@mcp.tool(
    name="pages_append_content",
    annotations={**WRITE, "title": "Append content to Wiki page"},
    tags=WRITE_TAGS,
)
def append_content(
    page_id: Annotated[int, Field(description="Numeric id of the page to append to.")],
    body: Annotated[
        PageAppendContent,
        Field(
            description="What to append and where: required ``content`` (YFM fragment) plus "
            "optional ``body`` (top/bottom), ``section`` or ``anchor`` placement."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> PageDetails:
    """Append a YFM fragment to a wiki page without rewriting the whole body.

    Unlike ``pages_update`` (full replace), this adds ``body.content`` at the chosen spot:
    ``body.body.location`` (top/bottom of the page), a numbered ``body.section``, or a named
    text ``body.anchor``. Returns the updated page.

    Example:
        >>> append_content(
        ...     page_id=12345, body={"content": "## More", "body": {"location": "bottom"}}
        ... )  # doctest: +SKIP
    """
    return client.pages.append_content(page_id=page_id, body=body.model_dump(exclude_none=True))


@mcp.tool(name="pages_clone", annotations={**WRITE, "title": "Clone Wiki page"}, tags=WRITE_TAGS)
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
) -> PageCloneOperation:
    """Copy a page to a new address (``POST /pages/{id}/clone`` — asynchronous).

    Cloning is the only way to give content a new slug (slugs are permanent). The call
    returns a deferred operation reference — poll ``operations_clone_get`` with the
    returned ``operation.id`` until it reaches a terminal status.

    Example:
        >>> clone(page_id=12345, body={"target": "data/y"})  # doctest: +SKIP
    """
    return client.pages.clone(page_id=page_id, body=body.model_dump(exclude_none=True))
