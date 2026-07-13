"""Tracker priorities FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)
from ycli.yandex.tracker.priorities.models import (
    Priority,
    PriorityCreate,
    PriorityList,
    PriorityUpdate,
)

mcp = FastMCP("tracker-priorities")


@mcp.tool(name="priorities_list", annotations={**RO, "title": "List Tracker priorities"}, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> PriorityList:
    """All available issue priorities in the organisation."""
    return client.priorities.list()


@mcp.tool(
    name="priorities_create",
    annotations={**WRITE, "title": "Create Tracker priority"},
    tags=WRITE_TAGS,
)
def create(body: PriorityCreate, client: TrackerClient = Depends(tracker_client)) -> Priority:
    """Create an org-global issue priority.

    CAUTION: priorities are organisation-wide and have no delete endpoint — creation leaves
    permanent residue. ``key`` is the latin identifier; ``name`` holds the ru/en display names.
    """
    return client.priorities.create(body)


@mcp.tool(
    name="priorities_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker priority"},
    tags=WRITE_TAGS,
)
def edit(
    priority_id: str,
    body: PriorityUpdate,
    version: int | None = None,
    client: TrackerClient = Depends(tracker_client),
) -> Priority:
    """Edit an issue priority; only the fields set in ``body`` are changed.

    ``priority_id`` is the numeric id (not the key). Pass ``version`` to guard against
    concurrent edits (optimistic locking).
    """
    return client.priorities.edit(priority_id, body, version=version)
