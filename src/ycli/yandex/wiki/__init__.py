"""Yandex Wiki domain — per-resource clients (pages/comments/attachments), CLI, and MCP."""

from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.service import Service

SERVICE = Service(
    name="wiki",
    help="Yandex Wiki: pages, grids, comments, attachments.",
    client="ycli.yandex.wiki.client:WikiClient",
    cli="ycli.yandex.wiki.cli:app",
    mcp="ycli.yandex.wiki.mcp.server:mcp",
    start="wiki_pages_get",
    profile=ServiceProfile("https://api.wiki.yandex.net/v1"),
    pagination="ycli.yandex.wiki.cursor:WIKI_CURSOR",
)
