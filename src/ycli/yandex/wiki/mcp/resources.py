"""Wiki MCP resources: what a user attaches, each repeating one read tool."""

from fastmcp.dependencies import Depends

from ycli.yandex.mcp import REPEATS_TOOL, guide, new_server
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import TAGS, wiki_client
from ycli.yandex.wiki.pages.mcp import get as pages_get

mcp = new_server("wiki-resources")


@mcp.resource(
    "ycli://page/{slug*}",
    name="page",
    title="Wiki page",
    mime_type="text/markdown",
    tags=TAGS,
    meta={REPEATS_TOOL: "wiki_pages_get"},
)
def page(slug: str, client: WikiClient = Depends(wiki_client)) -> str:
    """One Wiki page's Markdown body by slug (team/onboarding), as ``wiki_pages_get`` returns it."""
    return pages_get(slug, client=client)


@mcp.resource(
    "ycli://guide",
    name="guide",
    title="How to work with Yandex Wiki through ycli",
    mime_type="text/markdown",
    tags=TAGS,
)
def wiki_guide() -> str:
    """How to work with Yandex Wiki through these tools: what to call for what, and the traps."""
    return guide("ycli.yandex.wiki.mcp")
