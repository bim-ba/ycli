"""Tracker statuses FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

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
from ycli.yandex.tracker.statuses.models import Status, StatusCreate, StatusList, StatusUpdate

mcp = FastMCP("tracker-statuses")


@mcp.tool(name="statuses_list", annotations={**RO, "title": "List Tracker statuses"}, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> StatusList:
    """Every issue status configured in the organisation's workflows (key, name, and type such
    as new/inProgress/done). Use this to resolve or validate a status key before filtering or
    transitioning issues; see ``resolutions_list`` for close-out results and ``priorities_list``
    for priorities.

    >>> statuses_list()  # doctest: +SKIP
    """
    return client.statuses.list()


@mcp.tool(
    name="statuses_create", annotations={**WRITE, "title": "Create Tracker status"}, tags=WRITE_TAGS
)
def create(body: StatusCreate, client: TrackerClient = Depends(tracker_client)) -> Status:
    """Create an org-global issue status for use in workflows.

    CAUTION: statuses are organisation-wide and have no delete endpoint — creation leaves
    permanent residue. ``key`` is the latin identifier, ``name`` holds the ru/en display names,
    ``type`` is the stage kind (``new``/``inProgress``/``paused``/``done``/``cancelled``).
    """
    return client.statuses.create(body)


@mcp.tool(
    name="statuses_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker status"},
    tags=WRITE_TAGS,
)
def edit(
    status_id: str,
    body: StatusUpdate,
    version: int | None = None,
    client: TrackerClient = Depends(tracker_client),
) -> Status:
    """Edit an issue status; only the fields set in ``body`` are changed.

    ``status_id`` is the numeric id (not the key). Pass ``version`` to guard against concurrent
    edits (optimistic locking).
    """
    return client.statuses.edit(status_id, body, version=version)
