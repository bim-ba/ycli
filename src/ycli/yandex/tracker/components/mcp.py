"""Tracker components FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.components.models import ComponentList
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client

mcp = FastMCP("tracker-components")


@mcp.tool(name="components_list", annotations={**RO, "title": "List Tracker components"}, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> ComponentList:
    """All components created by the organisation's users, each with its queue, owner and
    description. Components are sub-areas used to classify issues within a queue; use this to
    discover valid component names/ids before filtering or creating issues.

    >>> components_list()  # doctest: +SKIP
    """
    return client.components.list()
