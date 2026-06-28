"""Tracker issue-links FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.links.models import LinkList

mcp = FastMCP("tracker-links")


@mcp.tool(name="links_list", annotations={**RO, "title": "List Tracker issue links"}, tags=TAGS)
def list_(key: str, client: TrackerClient = Depends(tracker_client)) -> LinkList:  # noqa: B008 — FastMCP resolves Depends at call time, not definition time
    """All links on a Tracker issue (linked issues, type, direction)."""
    return client.links.list(key)
