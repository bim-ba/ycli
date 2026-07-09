"""Tracker sprints FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.sprints.models import Sprint, SprintList

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
