"""Tracker MCP resources: what a user attaches, each repeating one read tool."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from fastmcp.resources import ResourceContent

from ycli.yandex.mcp import REPEATS_TOOL, guide
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import TAGS, tracker_client
from ycli.yandex.tracker.issues.mcp import get as issues_get

mcp = FastMCP("tracker-resources")


@mcp.resource(
    "ycli://issue/{key}",
    name="issue",
    title="Tracker issue",
    mime_type="application/json",
    tags=TAGS,
    meta={REPEATS_TOOL: "tracker_issues_get"},
)
def issue(key: str, client: TrackerClient = Depends(tracker_client)) -> list[ResourceContent]:
    """One Tracker issue by key (QUEUE-123), as ``tracker_issues_get`` returns it."""
    return [ResourceContent(issues_get(key, client=client))]


@mcp.resource(
    "ycli://guide",
    name="guide",
    title="How to work with Yandex Tracker through ycli",
    mime_type="text/markdown",
    tags=TAGS,
)
def tracker_guide() -> str:
    """How to work with Yandex Tracker through these tools: what to call for what, and the traps."""
    return guide("ycli.yandex.tracker.mcp")
