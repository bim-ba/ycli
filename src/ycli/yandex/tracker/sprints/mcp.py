"""Tracker sprints FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack
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
from ycli.yandex.tracker.sprints.models import Sprint, SprintCreate, SprintList, SprintUpdate

mcp = FastMCP("tracker-sprints")


@mcp.tool(name="sprints_list", annotations={**RO, "title": "List Tracker board sprints"}, tags=TAGS)
def list_(
    board_id: Annotated[
        int, Field(description="Numeric identifier of the board whose sprints to list.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> SprintList:
    """Every sprint defined on the given agile board, in the order Tracker returns them, each with
    its status, planned dates and parent board. Use this to enumerate a board's sprints; use
    ``sprints_get`` when you already know a sprint id, and ``boards_get`` for the board itself.

    >>> sprints_list(board_id=3)  # doctest: +SKIP
    """
    return client.sprints.list(board_id=board_id)


@mcp.tool(name="sprints_get", annotations={**RO, "title": "Get Tracker sprint"}, tags=TAGS)
def get(
    sprint_id: Annotated[int, Field(description="Numeric identifier of the sprint.")],
    client: TrackerClient = Depends(tracker_client),
) -> Sprint:
    """Look up a single sprint by its numeric id, including its status, planned start/end dates,
    actual start/end datetimes and parent board. Use this when you already know the sprint id; use
    ``sprints_list`` to enumerate all sprints on a board.

    >>> sprints_get(sprint_id=4405)  # doctest: +SKIP
    """
    return client.sprints.get(sprint_id=sprint_id)


@mcp.tool(
    name="sprints_create", annotations={**WRITE, "title": "Create Tracker sprint"}, tags=WRITE_TAGS
)
def create(body: SprintCreate, client: TrackerClient = Depends(tracker_client)) -> Sprint:
    """Create a sprint on an agile board; returns the new sprint.

    Required fields: ``name``, ``board`` (``{"id": "<board id>"}``), ``start_date`` and
    ``end_date`` (``YYYY-MM-DD``). The board must have sprints enabled.
    """
    return client.sprints.create(body)


@mcp.tool(
    name="sprints_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker sprint"},
    tags=WRITE_TAGS,
)
def edit(
    sprint_id: int,
    body: SprintUpdate,
    version: int | None = None,
    client: TrackerClient = Depends(tracker_client),
) -> Sprint:
    """Edit a sprint; only the fields set in ``body`` (name, dates) are changed.

    Get ``sprint_id`` from ``sprints_list``. Pass ``version`` (the sprint's current version,
    from ``sprints_get``) — the API requires it for optimistic locking and answers 428 without
    one. Returns the updated sprint.
    """
    return client.sprints.edit(sprint_id, body, version=version)


@mcp.tool(
    name="sprints_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker sprint"},
    tags=WRITE_TAGS,
)
def delete(sprint_id: int, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete a sprint (irreversible; its issues are not affected).

    Returns an acknowledgement on success.
    """
    client.sprints.delete(sprint_id=sprint_id)
    return Ack(detail=f"deleted sprint {sprint_id}")


@mcp.tool(
    name="sprints_start", annotations={**WRITE, "title": "Start Tracker sprint"}, tags=WRITE_TAGS
)
def start(
    sprint_id: int,
    version: int | None = None,
    client: TrackerClient = Depends(tracker_client),
) -> Sprint:
    """Start a sprint (sets its status to ``inProgress`` and stamps the actual start time).

    Pass ``version`` (the sprint's current version, from ``sprints_get``) — the API requires
    it for optimistic locking and answers 428 without one. Returns the updated sprint.
    """
    return client.sprints.start(sprint_id=sprint_id, version=version)


@mcp.tool(
    name="sprints_archive",
    annotations={**WRITE, "title": "Archive Tracker sprint"},
    tags=WRITE_TAGS,
)
def archive(
    sprint_id: int,
    version: int | None = None,
    client: TrackerClient = Depends(tracker_client),
) -> Sprint:
    """Archive a finished sprint (hides it from the board's active sprint list).

    Pass ``version`` (the sprint's current version, from ``sprints_get``) — the API requires
    it for optimistic locking and answers 428 without one. Returns the updated sprint.
    """
    return client.sprints.archive(sprint_id=sprint_id, version=version)
