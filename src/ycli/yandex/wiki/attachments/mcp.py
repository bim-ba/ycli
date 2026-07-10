"""Wiki /pages/{id}/attachments FastMCP tool."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.settings import AppConfig
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.wiki.attachments.models import AttachmentList
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, TAGS, app_config, wiki_client

mcp = FastMCP("wiki-attachments")


@mcp.tool(name="attachments_list", annotations={**RO, "title": "List Wiki attachments"}, tags=TAGS)
def list_(
    page_id: int,
    limit: int = 0,
    client: WikiClient = Depends(wiki_client),
    cfg: AppConfig = Depends(app_config),
) -> AttachmentList:
    """Attachments (name, size, mime type) on a page id, auto-paginated (drains ``next_cursor``).

    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given. This is the list surface;
    downloading an attachment's bytes is CLI/SDK-only (binary blobs are not an MCP payload).
    """
    cap = resolve_cap(limit, cfg.max_items)
    return client.attachments.list(page_id=page_id, limit=cap)
