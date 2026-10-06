"""Tracker external-applications FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, tracker_client
from ycli.yandex.tracker.models import Application

mcp = FastMCP("tracker-applications")


@mcp.tool(
    name="applications_list",
    annotations={**RO, "title": "List Tracker external applications"},
)
def list_(client: TrackerClient = Depends(tracker_client)) -> ItemList[Application]:
    """External applications that Tracker issues can be linked to via external links.

    Use this to discover which application ids/types are available before creating an external
    link; each application's id and type values are identical.
    """
    return client.applications.list()
