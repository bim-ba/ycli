"""Tracker worklog FastMCP tool (reads-only)."""
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.worklog.models import WorklogList

mcp = FastMCP("tracker-worklog")


@mcp.tool(name="worklog_list", annotations=RO, tags=TAGS)
def list_(key: str, client: TrackerClient = Depends(tracker_client)) -> WorklogList:
    """Time-tracking entries logged against a Tracker issue."""
    return client.worklog.list(key)
