"""Tracker issue-types FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

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
from ycli.yandex.tracker.issuetypes.models import (
    IssueType,
    IssueTypeCreate,
    IssueTypeList,
    IssueTypeUpdate,
)

mcp = FastMCP("tracker-issuetypes")


@mcp.tool(
    name="issuetypes_list", annotations={**RO, "title": "List Tracker issue types"}, tags=TAGS
)
def list_(client: TrackerClient = Depends(tracker_client)) -> IssueTypeList:
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
    name="issuetypes_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker issue type"},
    tags=WRITE_TAGS,
)
def edit(
    issue_type_id: str,
    body: IssueTypeUpdate,
    version: int | None = None,
    client: TrackerClient = Depends(tracker_client),
) -> IssueType:
    """Edit an org-global issue type; only the fields set in ``body`` are changed.

    ``issue_type_id`` is the numeric id (not the key). Pass ``version`` to guard against
    concurrent edits (optimistic locking).
    """
    return client.issuetypes.edit(issue_type_id, body, version=version)
