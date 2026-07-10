"""Tracker issue-checklists FastMCP tool (reads-only).

Only the checklist read is exposed here; every checklist mutation (add/edit/delete/clear)
ships on the CLI/SDK only, per ARCH-3 (the MCP server is read-only).
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.checklists.models import ChecklistItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client

mcp = FastMCP("tracker-checklists")


@mcp.tool(
    name="checklists_get", annotations={**RO, "title": "Get Tracker issue checklist"}, tags=TAGS
)
def get(
    key: Annotated[str, Field(description="Issue key, e.g. QUEUE-123.")],
    client: TrackerClient = Depends(tracker_client),
) -> ChecklistItemList:
    """The checklist items on a Tracker issue (text, done flag, assignee, per-item deadline).

    Returns a flat array; an issue with no checklist yields an empty list. Use this to read
    progress before mutating — item ids from here feed the CLI ``checklists edit/delete``
    (writes are CLI/SDK only, never MCP).

    Example:
        >>> get(key="QUEUE-123")  # doctest: +SKIP
    """
    return client.checklists.get(key)
