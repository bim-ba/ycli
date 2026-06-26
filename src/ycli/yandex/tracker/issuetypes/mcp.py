"""Tracker issue-types FastMCP tool (reads-only)."""
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issuetypes.models import IssueTypeList

mcp = FastMCP("tracker-issuetypes")


@mcp.tool(name="issuetypes_list", annotations=RO, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> IssueTypeList:
    """All available issue types (e.g. task, bug, epic)."""
    return client.issuetypes.list()
