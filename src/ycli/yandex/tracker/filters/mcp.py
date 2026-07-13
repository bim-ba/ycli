"""Tracker filters FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)
from ycli.yandex.tracker.filters.models import Filter, FilterCreate, FilterUpdate

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


@mcp.tool(
    name="filters_create", annotations={**WRITE, "title": "Create Tracker filter"}, tags=WRITE_TAGS
)
def create(body: FilterCreate, client: TrackerClient = Depends(tracker_client)) -> Filter:
    """Create a saved issue filter owned by the calling user.

    ``name`` is required; set ``query`` (a TQL string) or ``filter`` (a conditions object) for
    the stored search. NOTE: filters have no delete endpoint — the filter stays on the account.
    """
    return client.filters.create(body)


@mcp.tool(
    name="filters_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker filter"},
    tags=WRITE_TAGS,
)
def edit(
    filter_id: str, body: FilterUpdate, client: TrackerClient = Depends(tracker_client)
) -> Filter:
    """Edit a saved issue filter; only the fields set in ``body`` are changed.

    Get ``filter_id`` from ``filters_get`` / the Tracker UI. Returns the updated filter.
    """
    return client.filters.edit(filter_id, body)
