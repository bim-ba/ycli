"""Tracker issue-transitions FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    WRITE,
    IssueKey,
    new_server,
    tracker_client,
)
from ycli.yandex.tracker.transitions.models import Transition, TransitionExecute

mcp = new_server("tracker-transitions")


@mcp.tool(
    name="transitions_list",
    annotations={**RO, "title": "List Tracker issue transitions"},
)
def list_(
    issue_key: IssueKey, client: TrackerClient = Depends(tracker_client)
) -> ItemList[Transition]:
    """Available workflow transitions for a Tracker issue."""
    return client.transitions.list(issue_key)


@mcp.tool(
    name="transitions_execute",
    annotations={**WRITE, "title": "Execute Tracker issue transition"},
)
def execute(
    issue_key: IssueKey,
    transition_id: Annotated[str, Field(description="Transition id, from ``transitions_list``.")],
    body: TransitionExecute,
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Transition]:
    """Move a Tracker issue through a workflow transition (change its status).

    Get ``transition_id`` from ``transitions_list``. ``body`` may be empty or carry issue
    fields to set on transition, e.g. a resolution when closing. Returns the transitions
    available from the new status.
    """
    return client.transitions.execute(issue_key, transition_id, body)
