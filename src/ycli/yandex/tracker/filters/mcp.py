"""Tracker filters FastMCP tool (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.filters.models import Filter

mcp = FastMCP("tracker-filters")


@mcp.tool(name="filters_get", annotations={**RO, "title": "Get Tracker filter"}, tags=TAGS)
def get(
    filter_id: Annotated[
        str, Field(description="Numeric identifier of the saved filter, e.g. 12345.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Filter:
    """Parameters of a single saved issue filter: its stored conditions, query-language string,
    owner, favourite flag and access permissions. Use this to inspect a filter a user references
    by id; the resulting conditions can then feed an ``issues_search`` query.

    >>> filters_get(filter_id="12345")  # doctest: +SKIP
    """
    return client.filters.get(filter_id=filter_id)
