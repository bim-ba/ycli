"""Wiki FastMCP subserver — mounts the per-resource tool servers."""
from fastmcp import FastMCP

from ycli.yandex.wiki.attachments.mcp import mcp as attachments_mcp
from ycli.yandex.wiki.comments.mcp import mcp as comments_mcp
from ycli.yandex.wiki.pages.mcp import mcp as pages_mcp

mcp = FastMCP(
    "wiki",
    instructions=(
        "Read-only Yandex Wiki. Pages are addressed by their permanent slug: pages_get "
        "fetches content, pages_meta the metadata, pages_descendants the child tree."
    ),
)
mcp.mount(pages_mcp)
mcp.mount(comments_mcp)
mcp.mount(attachments_mcp)
