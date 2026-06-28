"""Tracker priorities FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.priorities.models import PriorityList

mcp = FastMCP("tracker-priorities")


@mcp.tool(name="priorities_list", annotations={**RO, "title": "List Tracker priorities"}, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> PriorityList:  # noqa: B008 — FastMCP resolves Depends at call time, not definition time
    """All available issue priorities in the organisation."""
    return client.priorities.list()
