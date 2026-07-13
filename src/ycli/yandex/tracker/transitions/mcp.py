"""Tracker issue-transitions FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, WRITE, WRITE_TAGS, tracker_client
from ycli.yandex.tracker.transitions.models import TransitionExecute, TransitionList

mcp = FastMCP("tracker-transitions")


@mcp.tool(
    name="transitions_list",
    annotations={**RO, "title": "List Tracker issue transitions"},
    tags=TAGS,
)
def list_(key: str, client: TrackerClient = Depends(tracker_client)) -> TransitionList:
    """Available workflow transitions for a Tracker issue."""
    return client.transitions.list(key)


@mcp.tool(
    name="transitions_execute",
    annotations={**WRITE, "title": "Execute Tracker issue transition"},
    tags=WRITE_TAGS,
)
def execute(
    key: str,
    transition_id: str,
    body: TransitionExecute,
    client: TrackerClient = Depends(tracker_client),
) -> TransitionList:
    """Move a Tracker issue through a workflow transition (change its status).

    Get ``transition_id`` from ``transitions_list``. ``body`` may be empty or carry issue
    fields to set on transition, e.g. a resolution when closing. Returns the transitions
    available from the new status.
    """
    return client.transitions.execute(key, transition_id, body.model_dump(exclude_none=True))
