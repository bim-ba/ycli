"""Tracker issue-checklists FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.checklists.models import (
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
    ChecklistItemID,
    IssueKey,
    new_server,
    tracker_client,
)
from ycli.yandex.tracker.models import Issue

mcp = new_server("tracker-checklists")


@mcp.tool(name="checklists_list", annotations={**RO, "title": "Get Tracker issue checklist"})
def list_(
    issue_key: Annotated[str, Field(description="Issue key, e.g. QUEUE-123.")],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[ChecklistItem]:
    """The checklist items on a Tracker issue (text, done flag, assignee, per-item deadline).

    Returns a flat array; an issue with no checklist yields an empty list. Item ids from here
    feed ``checklists_update`` / ``checklists_delete``.
    """
    return client.checklists.list(issue_key)


@mcp.tool(
    name="checklists_create",
    annotations={**WRITE, "title": "Add Tracker checklist item"},
)
def create(
    issue_key: IssueKey, body: ChecklistItemCreate, client: TrackerClient = Depends(tracker_client)
) -> Issue:
    """Add an item to a Tracker issue's checklist (creates the checklist if absent).

    Returns the issue with its full checklist.
    """
    return client.checklists.create(issue_key, body)


@mcp.tool(
    name="checklists_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker checklist item"},
)
def update(
    issue_key: IssueKey,
    item_id: ChecklistItemID,
    body: ChecklistItemUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Issue:
    """Edit one checklist item on a Tracker issue (text, checked state, assignee, deadline).

    Get ``item_id`` from ``checklists_list``. Returns the issue with its updated checklist.
    """
    return client.checklists.update(issue_key, item_id, body)


@mcp.tool(
    name="checklists_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker checklist item"},
)
def delete(
    issue_key: IssueKey, item_id: ChecklistItemID, client: TrackerClient = Depends(tracker_client)
) -> Issue:
    """Permanently remove one item from a Tracker issue's checklist (irreversible).

    Get ``item_id`` from ``checklists_list``. Returns the issue with its remaining checklist.
    """
    return client.checklists.delete(issue_key, item_id)


@mcp.tool(
    name="checklists_clear",
    annotations={**DESTRUCTIVE, "title": "Clear Tracker issue checklist"},
)
def clear(issue_key: IssueKey, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """Permanently delete the ENTIRE checklist of a Tracker issue (all items, irreversible).

    Returns the issue without its checklist.
    """
    return client.checklists.clear(issue_key)
