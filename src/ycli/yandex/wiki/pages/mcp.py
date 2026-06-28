"""Wiki /pages FastMCP tools — pure, DI via Depends, native error handling."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.settings import AppConfig
from ycli.yandex.wiki._deps import RO, TAGS, app_config, wiki_client
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.pages.models import PageDetails, PageRefList

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
    cap = limit or cfg.max_items
    return client.pages.descendants(slug=slug, limit=cap)
