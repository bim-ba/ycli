"""Tracker issue-comments FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.comments.models import CommentList
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client

mcp = FastMCP("tracker-comments")


@mcp.tool(
    name="comments_list", annotations={**RO, "title": "List Tracker issue comments"}, tags=TAGS
)
def list_(key: str, client: TrackerClient = Depends(tracker_client)) -> CommentList:
    """All comments on a Tracker issue."""
    return client.comments.list(key)
