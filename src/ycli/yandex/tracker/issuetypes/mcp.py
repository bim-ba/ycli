"""Tracker issue-types FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    Version,
    tracker_client,
)
from ycli.yandex.tracker.issuetypes.models import IssueType, IssueTypeCreate, IssueTypeUpdate

mcp = FastMCP("tracker-issuetypes")


@mcp.tool(
    name="issuetypes_list", annotations={**RO, "title": "List Tracker issue types"}, tags=TAGS
)
def list_(client: TrackerClient = Depends(tracker_client)) -> ItemList[IssueType]:
    """All available issue types (e.g. task, bug, epic)."""
    return client.issuetypes.list()


@mcp.tool(
    name="issuetypes_create",
    annotations={**WRITE, "title": "Create Tracker issue type"},
    tags=WRITE_TAGS,
)
def create(body: IssueTypeCreate, client: TrackerClient = Depends(tracker_client)) -> IssueType:
    """Create an org-global issue type (e.g. a new kind of task).

    CAUTION: issue types are organisation-wide and have no delete endpoint — creation leaves
    permanent residue. ``key`` is the latin identifier; ``name`` holds the ru/en display names.
    """
    return client.issuetypes.create(body)


@mcp.tool(
    name="issuetypes_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker issue type"},
    tags=WRITE_TAGS,
)
def update(
    issue_type_id: Annotated[
        str, Field(description="Issue type id or key, from ``issuetypes_list``.")
    ],
    body: IssueTypeUpdate,
    version: Version = None,
    client: TrackerClient = Depends(tracker_client),
) -> IssueType:
    """Edit an org-global issue type; only the fields set in ``body`` are changed.

    ``issue_type_id`` is the numeric id (not the key). Pass ``version`` to guard against
    concurrent edits (optimistic locking).
    """
    return client.issuetypes.update(issue_type_id, body, version=version)
