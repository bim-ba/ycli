"""Yandex Tracker domain — per-resource clients (issues, comments, links, …), CLI, and MCP."""

from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.service import Service

SERVICE = Service(
    name="tracker",
    help="Yandex Tracker: issues, queues, boards, sprints, fields, automation.",
    client="ycli.yandex.tracker.client:TrackerClient",
    cli="ycli.yandex.tracker.cli:app",
    mcp="ycli.yandex.tracker.mcp.server:mcp",
    profile=ServiceProfile("https://api.tracker.yandex.net/v3"),
    pagination="ycli.yandex.tracker.pages:LINK_NEXT",
)
