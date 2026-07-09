"""Tracker external-applications FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.applications.models import ApplicationList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client

mcp = FastMCP("tracker-applications")


@mcp.tool(
    name="applications_list",
    annotations={**RO, "title": "List Tracker external applications"},
    tags=TAGS,
)
def list_(client: TrackerClient = Depends(tracker_client)) -> ApplicationList:
    """External applications that Tracker issues can be linked to via external links. Use this to
    discover which application ids/types are available before creating an external link; each
    application's id and type values are identical.

    >>> applications_list()  # doctest: +SKIP
    """
    return client.applications.list()
