"""Tracker issue-checklists FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.checklists.models import (
    Checklist,
    ChecklistItem,
    ChecklistItemCreate,
    ChecklistItemUpdate,
)
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    ChecklistItemId,
    IssueKey,
    tracker_client,
)

mcp = FastMCP("tracker-checklists")


@mcp.tool(name="checklists_get", annotations={**RO, "title": "Get Tracker issue checklist"})
def get(
    key: Annotated[str, Field(description="Issue key, e.g. QUEUE-123.")],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[ChecklistItem]:
    """The checklist items on a Tracker issue (text, done flag, assignee, per-item deadline).

    Returns a flat array; an issue with no checklist yields an empty list. Item ids from here
    feed ``checklists_update`` / ``checklists_delete``.
    """
    return client.checklists.get(key)


@mcp.tool(
    name="checklists_create",
    annotations={**WRITE, "title": "Add Tracker checklist item"},
)
def create(
    key: IssueKey, body: ChecklistItemCreate, client: TrackerClient = Depends(tracker_client)
) -> Checklist:
    """Add an item to a Tracker issue's checklist (creates the checklist if absent).

    Returns the issue with its full checklist.
    """
    return client.checklists.create(key, body)


@mcp.tool(
    name="checklists_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker checklist item"},
)
def update(
    key: IssueKey,
    item_id: ChecklistItemId,
    body: ChecklistItemUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Checklist:
    """Edit one checklist item on a Tracker issue (text, checked state, assignee, deadline).

    Get ``item_id`` from ``checklists_get``. Returns the issue with its updated checklist.
    """
    return client.checklists.update(key, item_id, body)


@mcp.tool(
    name="checklists_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker checklist item"},
)
def delete(
    key: IssueKey, item_id: ChecklistItemId, client: TrackerClient = Depends(tracker_client)
) -> Checklist:
    """Permanently remove one item from a Tracker issue's checklist (irreversible).

    Get ``item_id`` from ``checklists_get``. Returns the issue with its remaining checklist.
    """
    return client.checklists.delete(key, item_id)


@mcp.tool(
    name="checklists_clear",
    annotations={**DESTRUCTIVE, "title": "Clear Tracker issue checklist"},
)
def clear(key: IssueKey, client: TrackerClient = Depends(tracker_client)) -> Checklist:
    """Permanently delete the ENTIRE checklist of a Tracker issue (all items, irreversible).

    Returns the issue without its checklist.
    """
    return client.checklists.clear(key)
