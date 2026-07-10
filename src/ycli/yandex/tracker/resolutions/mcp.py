"""Tracker resolutions FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.resolutions.models import ResolutionList

mcp = FastMCP("tracker-resolutions")


@mcp.tool(
    name="resolutions_list", annotations={**RO, "title": "List Tracker resolutions"}, tags=TAGS
)
def list_(client: TrackerClient = Depends(tracker_client)) -> ResolutionList:
    """Every issue resolution configured in the organisation (the close-out result such as
    fixed/duplicate/won't-fix). Use this to resolve or validate a resolution key when reading a
    closed issue or filtering; see ``statuses_list`` for workflow stages, not close-out reasons.

    >>> resolutions_list()  # doctest: +SKIP
    """
    return client.resolutions.list()
