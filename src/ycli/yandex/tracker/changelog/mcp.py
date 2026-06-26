"""Tracker changelog FastMCP tool (reads-only)."""
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
from ycli.yandex.tracker.changelog.models import ChangelogList
from ycli.yandex.tracker.client import TrackerClient

mcp = FastMCP("tracker-changelog")


@mcp.tool(name="changelog_list", annotations=RO, tags=TAGS)
def list_(key: str, client: TrackerClient = Depends(tracker_client)) -> ChangelogList:
    """Full changelog (edit history) for a Tracker issue."""
    return client.changelog.list(key)
