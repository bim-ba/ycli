"""Tracker worklog FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.worklog.models import WorklogList

mcp = FastMCP("tracker-worklog")


@mcp.tool(name="worklog_list", annotations={**RO, "title": "List Tracker worklog"}, tags=TAGS)
def list_(key: str, client: TrackerClient = Depends(tracker_client)) -> WorklogList:
    """Time-tracking entries logged against a single Tracker issue.

    Scoped to one issue by ``key``. To search worklog across the whole org (by author and/or a
    creation-time range) use ``worklog_search`` instead.

    Example:
        >>> list_(key="QUEUE-123")  # doctest: +SKIP
    """
    return client.worklog.list(key)


@mcp.tool(name="worklog_search", annotations={**RO, "title": "Search Tracker worklog"}, tags=TAGS)
def search(
    created_by: Annotated[
        str | None, Field(description="Login or id of the record author to filter by.")
    ] = None,
    created_from: Annotated[
        str | None, Field(description="Start of the creation-time range (``YYYY-MM-DDThh:mm:ss``).")
    ] = None,
    created_to: Annotated[
        str | None, Field(description="End of the creation-time range (``YYYY-MM-DDThh:mm:ss``).")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> WorklogList:
    """Org-wide worklog entries filtered by author and/or a creation-time range.

    Unlike ``worklog_list`` (one issue), this searches every issue's worklog. Pass
    ``created_by`` to scope to a user and ``created_from`` / ``created_to`` for a time window;
    all are optional.

    Example:
        >>> search(created_by="veikus", created_from="2018-06-06T00:00:00")  # doctest: +SKIP
    """
    body: dict[str, object] = {}
    if created_by:
        body["createdBy"] = created_by
    created_at = {k: v for k, v in (("from", created_from), ("to", created_to)) if v}
    if created_at:
        body["createdAt"] = created_at
    return client.worklog.search(body)
