"""Tracker issue-checklists FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.checklists.models import (
    Checklist,
    ChecklistItemCreate,
    ChecklistItemList,
    ChecklistItemUpdate,
)
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)

mcp = FastMCP("tracker-checklists")


@mcp.tool(
    name="checklists_get", annotations={**RO, "title": "Get Tracker issue checklist"}, tags=TAGS
)
def get(
    key: Annotated[str, Field(description="Issue key, e.g. QUEUE-123.")],
    client: TrackerClient = Depends(tracker_client),
) -> ChecklistItemList:
    """The checklist items on a Tracker issue (text, done flag, assignee, per-item deadline).

    Returns a flat array; an issue with no checklist yields an empty list. Item ids from here
    feed ``checklists_edit`` / ``checklists_delete``.

    Example:
        >>> get(key="QUEUE-123")  # doctest: +SKIP
    """
    return client.checklists.get(key)


@mcp.tool(
    name="checklists_create",
    annotations={**WRITE, "title": "Add Tracker checklist item"},
    tags=WRITE_TAGS,
)
def create(
    key: str, body: ChecklistItemCreate, client: TrackerClient = Depends(tracker_client)
) -> Checklist:
    """Add an item to a Tracker issue's checklist (creates the checklist if absent).

    Returns the issue with its full checklist.
    """
    return client.checklists.create(key, body.model_dump(by_alias=True, exclude_none=True))


@mcp.tool(
    name="checklists_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker checklist item"},
    tags=WRITE_TAGS,
)
def edit(
    key: str,
    item_id: str,
    body: ChecklistItemUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Checklist:
    """Edit one checklist item on a Tracker issue (text, checked state, assignee, deadline).

    Get ``item_id`` from ``checklists_get``. Returns the issue with its updated checklist.
    """
    return client.checklists.edit(key, item_id, body.model_dump(by_alias=True, exclude_none=True))


@mcp.tool(
    name="checklists_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker checklist item"},
    tags=WRITE_TAGS,
)
def delete(key: str, item_id: str, client: TrackerClient = Depends(tracker_client)) -> Checklist:
    """Permanently remove one item from a Tracker issue's checklist (irreversible).

    Get ``item_id`` from ``checklists_get``. Returns the issue with its remaining checklist.
    """
    return client.checklists.delete(key, item_id)


@mcp.tool(
    name="checklists_clear",
    annotations={**DESTRUCTIVE, "title": "Clear Tracker issue checklist"},
    tags=WRITE_TAGS,
)
def clear(key: str, client: TrackerClient = Depends(tracker_client)) -> Checklist:
    """Permanently delete the ENTIRE checklist of a Tracker issue (all items, irreversible).

    Returns the issue without its checklist.
    """
    return client.checklists.clear(key)
