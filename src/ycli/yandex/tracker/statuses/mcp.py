"""Tracker statuses FastMCP tool (reads-only)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.statuses.models import StatusList

mcp = FastMCP("tracker-statuses")


@mcp.tool(name="statuses_list", annotations={**RO, "title": "List Tracker statuses"}, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> StatusList:
    """Every issue status configured in the organisation's workflows (key, name, and type such
    as new/inProgress/done). Use this to resolve or validate a status key before filtering or
    transitioning issues; see ``resolutions_list`` for close-out results and ``priorities_list``
    for priorities.

    >>> statuses_list()  # doctest: +SKIP
    """
    return client.statuses.list()
