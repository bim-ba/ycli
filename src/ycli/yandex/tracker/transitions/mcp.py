"""Tracker issue-transitions FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.transitions.models import TransitionList

mcp = FastMCP("tracker-transitions")


@mcp.tool(
    name="transitions_list",
    annotations={**RO, "title": "List Tracker issue transitions"},
    tags=TAGS,
)
def list_(key: str, client: TrackerClient = Depends(tracker_client)) -> TransitionList:  # noqa: B008 — FastMCP resolves Depends at call time, not definition time
    """Available workflow transitions for a Tracker issue."""
    return client.transitions.list(key)
