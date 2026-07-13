"""Tracker /issues FastMCP tools (reads + writes) — Depends DI, native error handling."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.models import Ack, require_found
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)
from ycli.yandex.tracker.issues.models import (
    Issue,
    IssueCreate,
    IssueList,
    IssueUpdate,
    ScrollClear,
)
from ycli.yandex.tracker.utils import count_body

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
    return require_found(
        result,
        sentinel=lambda r: r.key is None,
        message=f"issue {key!r} not found (got empty response — check key or permissions)",
    )


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
def count(
    query: str = "",
    queue: str = "",
    status: str = "",
    client: TrackerClient = Depends(tracker_client),
) -> int:
    """Count of issues matching a TQL query or filters.

    Pass ``query`` for a TQL query string (takes precedence over filters), or pass
    ``queue``/``status`` to filter by those fields.  With no arguments the API counts
    every issue in the org.
    """
    return client.issues.count(body=count_body(query=query, queue=queue, status=status))


@mcp.tool(
    name="issues_suggest",
    annotations={**RO, "title": "Suggest Tracker issues by title"},
    tags=TAGS,
)
def suggest(text: str, client: TrackerClient = Depends(tracker_client)) -> IssueList:
    """Typeahead over visible issues — issues whose summary contains ``text``.

    A lightweight title match; for full TQL search use ``issues_search``.
    """
    return client.issues.suggest(text)


@mcp.tool(
    name="issues_create", annotations={**WRITE, "title": "Create Tracker issue"}, tags=WRITE_TAGS
)
def create(body: IssueCreate, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """Create a Tracker issue; returns the new issue with its key."""
    return client.issues.create(body.model_dump(exclude_none=True))


@mcp.tool(
    name="issues_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Tracker issue"},
    tags=WRITE_TAGS,
)
def update(key: str, body: IssueUpdate, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """Update fields of a Tracker issue; only the keys present in ``body`` are changed.

    Status is NOT changed here — use ``transitions_execute``. Returns the updated issue.
    """
    return client.issues.update(key, body.model_dump(exclude_none=True))


@mcp.tool(name="issues_move", annotations={**WRITE, "title": "Move Tracker issue"}, tags=WRITE_TAGS)
def move(key: str, queue: str, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """Move a Tracker issue to another queue (it gets a new key there; the old key redirects).

    ``queue`` is the target queue key. Fields that do not exist in the target queue may be
    dropped. Returns the moved issue with its new key.
    """
    return client.issues.move(key, queue)


@mcp.tool(
    name="issues_scroll_clear",
    annotations={**WRITE_IDEMPOTENT, "title": "Clear Tracker search scroll"},
    tags=WRITE_TAGS,
)
def scroll_clear(body: ScrollClear, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Release the server resources of a scrolled issue search (harmless housekeeping).

    ``body`` maps each ``X-Scroll-Id`` to its ``X-Scroll-Token`` from a scrolled
    ``issues.search`` response. Returns an acknowledgement on success.
    """
    client.issues.scroll_clear(body.model_dump())
    return Ack.cleared("search scroll resources")
