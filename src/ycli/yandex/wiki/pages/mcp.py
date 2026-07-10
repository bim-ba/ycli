"""Wiki /pages FastMCP tools — pure, DI via Depends, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, TAGS, app_config, wiki_client
from ycli.yandex.wiki.pages.models import GridRefList, PageDetails, PageRefList

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
    cfg: AppConfig = Depends(app_config),
) -> PageRefList:
    """All descendant refs under SLUG, auto-paginated. Capped at YCLI_MAX_ITEMS (default 500)
    unless ``limit`` is given; narrow by SLUG for large trees."""
    cap = resolve_cap(limit, cfg.max_items)
    return client.pages.descendants(slug=slug, limit=cap)


@mcp.tool(name="pages_grids_list", annotations={**RO, "title": "List Wiki page grids"}, tags=TAGS)
def grids_list(
    page_id: Annotated[int, Field(description="Numeric page id whose grids to list.")],
    limit: Annotated[int, Field(description="Max grids (0 = YCLI_MAX_ITEMS cap).")] = 0,
    client: WikiClient = Depends(wiki_client),
    cfg: AppConfig = Depends(app_config),
) -> GridRefList:
    """Dynamic tables (grids) attached to a page id, auto-paginated (drains ``next_cursor``).

    Each grid ref is a UUID ``id`` + ``title`` + ``created_at``. Capped at YCLI_MAX_ITEMS
    (default 500) unless ``limit`` is given. Reads a page's numeric id — pair with
    ``pages_meta`` / ``pages_descendants`` (whose refs carry the ids) to find one.

    Example:
        >>> grids_list(page_id=12345, limit=50)  # doctest: +SKIP
    """
    cap = resolve_cap(limit, cfg.max_items)
    return client.pages.grids(page_id=page_id, limit=cap)
