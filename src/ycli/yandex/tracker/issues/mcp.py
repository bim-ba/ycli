"""Tracker /issues FastMCP tools (reads-only) — Depends DI, native error handling."""

from typing import Any

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.models import Issue, IssueList

mcp = FastMCP("tracker-issues")


@mcp.tool(name="issues_get", annotations={**RO, "title": "Get Tracker issue"}, tags=TAGS)
def get(key: str, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """A single Tracker issue by key (raises if not found).

    In production the Transport response hook raises ``YandexNotFoundError`` on a 404
    before this guard is reached. This check only fires for a 2xx response that carries
    an empty body (key=None) — an edge case unlikely in practice but defended here for
    safety (e.g. incorrect permissions returning a blank object instead of a 403).
    """
    result = client.issues.get(key)
    if result.key is None:
        raise ValueError(f"issue {key!r} not found (got empty response — check key or permissions)")
    return result


@mcp.tool(
    name="issues_full", annotations={**RO, "title": "Get full Tracker issue (raw)"}, tags=TAGS
)
def full(key: str, client: TrackerClient = Depends(tracker_client)) -> dict[str, Any]:
    """A single Tracker issue as a raw dict (all fields)."""
    return client.issues.get_raw(key)


@mcp.tool(name="issues_list", annotations={**RO, "title": "List Tracker issues"}, tags=TAGS)
def list_(
    queue: str = "",
    status: str = "",
    assignee: str = "",
    epic: str = "",
    type_: str = "",
    client: TrackerClient = Depends(tracker_client),
) -> IssueList:
    """Issues matching the supplied filters (omitted filters dropped)."""
    flt = {
        k: v
        for k, v in (
            ("queue", queue),
            ("status", status),
            ("assignee", assignee),
            ("epic", epic),
            ("type", type_),
        )
        if v
    }
    return client.issues.search(body={"filter": flt})


@mcp.tool(
    name="issues_search", annotations={**RO, "title": "Search Tracker issues (TQL)"}, tags=TAGS
)
def search(query: str, client: TrackerClient = Depends(tracker_client)) -> IssueList:
    """Issues matching a TQL query string."""
    return client.issues.search(body={"query": query})


@mcp.tool(name="issues_count", annotations={**RO, "title": "Count Tracker issues"}, tags=TAGS)
def count(query: str, client: TrackerClient = Depends(tracker_client)) -> int:
    """Count of issues matching a TQL query string."""
    return client.issues.count(body={"query": query})
