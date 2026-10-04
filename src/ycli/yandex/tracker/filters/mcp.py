"""Tracker filters FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    tracker_client,
)
from ycli.yandex.tracker.filters.models import Filter, FilterCreate, FilterUpdate

mcp = FastMCP("tracker-filters")


@mcp.tool(name="filters_get", annotations={**RO, "title": "Get Tracker filter"})
def get(
    filter_id: Annotated[
        str, Field(description="Numeric identifier of the saved filter, e.g. 12345.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Filter:
    """Parameters of a single saved issue filter.

    They include its stored conditions, query-language string, owner, favourite flag and access
    permissions. Use this to inspect a filter a user references by id; the resulting conditions
    can then feed an ``issues_search`` query.
    """
    return client.filters.get(filter_id=filter_id)


@mcp.tool(name="filters_create", annotations={**WRITE, "title": "Create Tracker filter"})
def create(body: FilterCreate, client: TrackerClient = Depends(tracker_client)) -> Filter:
    """Create a saved issue filter owned by the calling user.

    ``name`` is required; set ``query`` (a TQL string) or ``filter`` (a conditions object) for
    the stored search. Remove it later with ``filters_delete``.
    """
    return client.filters.create(body)


@mcp.tool(
    name="filters_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker filter"},
)
def update(
    filter_id: Annotated[
        str, Field(description="Identifier of the saved filter, from ``filters_get``.")
    ],
    body: FilterUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Filter:
    """Edit a saved issue filter; only the fields set in ``body`` are changed.

    Get ``filter_id`` from ``filters_get`` / the Tracker UI. Returns the updated filter.
    """
    return client.filters.update(filter_id, body)


@mcp.tool(
    name="filters_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker filter"},
)
def delete(
    filter_id: Annotated[
        str, Field(description="Numeric identifier of the saved filter, e.g. 12345.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Permanently delete a saved issue filter (irreversible).

    Returns an acknowledgement on success.
    """
    client.filters.delete(filter_id)
    return Ack.deleted("filter", filter_id)
