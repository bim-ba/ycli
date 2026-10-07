"""Tracker priorities FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    Version,
    new_server,
    tracker_client,
)
from ycli.yandex.tracker.priorities.models import Priority, PriorityCreate, PriorityUpdate

mcp = new_server("tracker-priorities")


@mcp.tool(name="priorities_list", annotations={**RO, "title": "List Tracker priorities"})
def list_(
    localized: Annotated[
        bool | None,
        Field(description="``false`` returns the names in every language."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Priority]:
    """All available issue priorities in the organisation."""
    return client.priorities.list(localized=localized)


@mcp.tool(
    name="priorities_create",
    annotations={**WRITE, "title": "Create Tracker priority"},
)
def create(body: PriorityCreate, client: TrackerClient = Depends(tracker_client)) -> Priority:
    """Create an org-global issue priority.

    CAUTION: priorities are organisation-wide and have no delete endpoint — creation leaves
    permanent residue. ``key`` is the latin identifier; ``name`` holds the ru/en display names.
    """
    return client.priorities.create(body)


@mcp.tool(
    name="priorities_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker priority"},
)
def update(
    priority_id: Annotated[str, Field(description="Priority id or key, from ``priorities_list``.")],
    body: PriorityUpdate,
    version: Version = None,
    client: TrackerClient = Depends(tracker_client),
) -> Priority:
    """Edit an issue priority; only the fields set in ``body`` are changed.

    ``priority_id`` is the numeric id (not the key). Pass ``version`` to guard against
    concurrent edits (optimistic locking).
    """
    return client.priorities.update(priority_id, body, version=version)
