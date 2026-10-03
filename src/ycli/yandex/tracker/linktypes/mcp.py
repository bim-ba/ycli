"""Tracker link-types FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.models import LinkType

mcp = FastMCP("tracker-linktypes")


@mcp.tool(name="linktypes_list", annotations={**RO, "title": "List Tracker link types"}, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> ItemList[LinkType]:
    """All available link types (e.g. relates, depends on, blocks)."""
    return client.linktypes.list()
