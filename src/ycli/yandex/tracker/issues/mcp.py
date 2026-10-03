"""Tracker /issues FastMCP tools (reads + writes) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList, require_found
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    LIMIT_CAP,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    IssueKey,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.issues.models import (
    Issue,
    IssueCreate,
    IssueUpdate,
    ScrollClear,
    count_body,
    filter_body,
)

mcp = FastMCP("tracker-issues")

_LIMIT = f"Max issues to return; {LIMIT_CAP}"


@mcp.tool(name="issues_get", annotations={**RO, "title": "Get Tracker issue"}, tags=TAGS)
def get(key: IssueKey, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """A single Tracker issue by key (raises if not found)."""
    result = client.issues.get(key)
    # The core session already raises on a 404; this guard only fires for a 2xx with an empty
    # body (key=None), e.g. missing permissions answered with a blank object instead of a 403.
    return require_found(
        result,
        sentinel=lambda r: r.key is None,
        message=f"issue {key!r} not found (got empty response — check key or permissions)",
    )


@mcp.tool(name="issues_list", annotations={**RO, "title": "List Tracker issues"}, tags=TAGS)
def list_(
    queue: Annotated[str, Field(description="Queue key, e.g. QUEUE.")] = "",
    status: Annotated[str, Field(description="Status key, e.g. open.")] = "",
    assignee: Annotated[str, Field(description="Assignee login or id.")] = "",
    epic: Annotated[str, Field(description="Epic issue key.")] = "",
    issue_type: Annotated[str, Field(description="Issue type key, e.g. bug or task.")] = "",
    limit: Annotated[int, Field(description=_LIMIT)] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Issue]:
    """Issues matching the supplied filters (omitted filters dropped), auto-paginated.

    Returns at most ``limit`` issues; exactly ``limit`` back means more may match — narrow the
    filters or raise ``limit``.
    """
    body = filter_body(queue=queue, status=status, assignee=assignee, epic=epic, type_=issue_type)
    return client.issues.search(body, limit=config.http.cap(limit))


@mcp.tool(
    name="issues_search", annotations={**RO, "title": "Search Tracker issues (TQL)"}, tags=TAGS
)
def search(
    query: Annotated[str, Field(description="TQL query, e.g. ``Queue: QUEUE Status: open``.")],
    limit: Annotated[int, Field(description=_LIMIT)] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Issue]:
    """Issues matching a TQL query string, auto-paginated.

    Returns at most ``limit`` issues; exactly ``limit`` back means more may match — refine the
    query or raise ``limit``.
    """
    return client.issues.search({"query": query}, limit=config.http.cap(limit))


@mcp.tool(name="issues_count", annotations={**RO, "title": "Count Tracker issues"}, tags=TAGS)
def count(
    query: Annotated[
        str, Field(description="TQL query; takes precedence over ``queue`` / ``status``.")
    ] = "",
    queue: Annotated[str, Field(description="Queue key to count issues in.")] = "",
    status: Annotated[str, Field(description="Status key to count issues in.")] = "",
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
def suggest(
    text: Annotated[str, Field(description="Text fragment to match in issue summaries.")],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Issue]:
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
def update(
    key: IssueKey, body: IssueUpdate, client: TrackerClient = Depends(tracker_client)
) -> Issue:
    """Update fields of a Tracker issue; only the keys present in ``body`` are changed.

    Status is NOT changed here — use ``transitions_execute``. Returns the updated issue.
    """
    return client.issues.update(key, body.model_dump(exclude_none=True))


@mcp.tool(name="issues_move", annotations={**WRITE, "title": "Move Tracker issue"}, tags=WRITE_TAGS)
def move(
    key: IssueKey,
    queue: Annotated[str, Field(description="Target queue key, e.g. NEW.")],
    client: TrackerClient = Depends(tracker_client),
) -> Issue:
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
