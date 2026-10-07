"""Tracker link-types FastMCP tool (reads-only)."""

from fastmcp.dependencies import Depends

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, new_server, tracker_client
from ycli.yandex.tracker.models import LinkType

mcp = new_server("tracker-linktypes")


@mcp.tool(name="linktypes_list", annotations={**RO, "title": "List Tracker link types"})
def list_(client: TrackerClient = Depends(tracker_client)) -> ItemList[LinkType]:
    """All available link types (e.g. relates, depends on, blocks)."""
    return client.linktypes.list()
