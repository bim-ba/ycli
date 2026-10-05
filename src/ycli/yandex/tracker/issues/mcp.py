"""Tracker /issues FastMCP tools (reads + writes) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.bulk.models import BulkChange, BulkMove, BulkTransition, BulkUpdate
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    Expand,
    IssueKey,
    Notify,
    NotifyAuthor,
    ReplyFields,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.issues.models import (
    ImportTask,
    Issue,
    IssueCreate,
    IssueSearch,
    IssueUpdate,
    ScrollClear,
    ScrollType,
    count_body,
    filter_body,
)

mcp = FastMCP("tracker-issues")

_LIMIT = f"Max issues to return; {LIMIT_CAP}"


@mcp.tool(name="issues_get", annotations={**RO, "title": "Get Tracker issue"})
def get(
    key: IssueKey,
    expand: Expand = None,
    fields: ReplyFields = None,
    client: TrackerClient = Depends(tracker_client),
) -> Issue:
    """A single Tracker issue by key."""
    return client.issues.get(key, expand=expand, fields=fields)


@mcp.tool(name="issues_list", annotations={**RO, "title": "List Tracker issues"})
def list_(
    queue: Annotated[str | None, Field(description="Queue key, e.g. QUEUE.")] = None,
    status: Annotated[str | None, Field(description="Status key, e.g. open.")] = None,
    assignee: Annotated[str | None, Field(description="Assignee login or id.")] = None,
    epic: Annotated[str | None, Field(description="Epic issue key.")] = None,
    issue_type: Annotated[
        str | None, Field(description="Issue type key, e.g. bug or task.")
    ] = None,
    limit: Annotated[int | None, Field(ge=1, description=_LIMIT)] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Issue]:
    """Issues matching the supplied filters (omitted filters dropped), auto-paginated.

    Returns at most ``limit`` issues; exactly ``limit`` back means more may match — narrow the
    filters or raise ``limit``.
    """
    # The tool's parameters say "not given" with an empty string; the body builder with None.
    body = filter_body(
        queue=queue,
        status=status,
        assignee=assignee,
        epic=epic,
        type_=issue_type,
    )
    return client.issues.search(body, limit=config.http.cap(limit))


@mcp.tool(name="issues_search", annotations={**RO, "title": "Search Tracker issues (TQL)"})
def search(
    query: Annotated[str, Field(description="TQL query, e.g. ``Queue: QUEUE Status: open``.")],
    limit: Annotated[int | None, Field(ge=1, description=_LIMIT)] = None,
    expand: Expand = None,
    scroll_type: Annotated[
        ScrollType | None,
        Field(description="Scroll through the results (no 10 000 cap)."),
    ] = None,
    per_scroll: Annotated[
        int | None, Field(description="Issues per scroll page (1000 at most).")
    ] = None,
    scroll_ttl_millis: Annotated[
        int | None, Field(description="How long the scroll stays open, in milliseconds.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Issue]:
    """Issues matching a TQL query string, auto-paginated.

    Returns at most ``limit`` issues; exactly ``limit`` back means more may match — refine the
    query or raise ``limit``.
    """
    return client.issues.search(
        IssueSearch(query=query),
        limit=config.http.cap(limit),
        expand=expand,
        scroll_type=scroll_type,
        per_scroll=per_scroll,
        scroll_ttl_millis=scroll_ttl_millis,
    )


@mcp.tool(name="issues_count", annotations={**RO, "title": "Count Tracker issues"})
def count(
    query: Annotated[
        str | None, Field(description="TQL query; takes precedence over ``queue`` / ``status``.")
    ] = None,
    queue: Annotated[str | None, Field(description="Queue key to count issues in.")] = None,
    status: Annotated[str | None, Field(description="Status key to count issues in.")] = None,
    client: TrackerClient = Depends(tracker_client),
) -> int:
    """Count of issues matching a TQL query or filters.

    Pass ``query`` for a TQL query string (takes precedence over filters), or pass
    ``queue``/``status`` to filter by those fields.  With no arguments the API counts
    every issue in the org.
    """
    body = count_body(query=query, queue=queue, status=status)
    return client.issues.count(body=body)


@mcp.tool(
    name="issues_suggest",
    annotations={**RO, "title": "Suggest Tracker issues by title"},
)
def suggest(
    text: Annotated[str, Field(description="Text fragment to match in issue summaries.")],
    queue: Annotated[str | None, Field(description="Key of the queue to search in.")] = None,
    full: Annotated[
        bool | None,
        Field(
            description="Return each issue in full; needed for ``fields``, ``expand``, ``embed``."
        ),
    ] = None,
    fields: ReplyFields = None,
    expand: Expand = None,
    embed: Annotated[
        str | None, Field(description="Blocks of ``expand`` to return in more detail.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Issue]:
    """Typeahead over visible issues — issues whose summary contains ``text``.

    A lightweight title match; for full TQL search use ``issues_search``.
    """
    return client.issues.suggest(
        text, queue=queue, full=full, fields=fields, expand=expand, embed=embed
    )


@mcp.tool(name="issues_create", annotations={**WRITE, "title": "Create Tracker issue"})
def create(
    body: IssueCreate, notify: Notify = None, client: TrackerClient = Depends(tracker_client)
) -> Issue:
    """Create a Tracker issue; returns the new issue with its key."""
    return client.issues.create(body, notify=notify)


@mcp.tool(
    name="issues_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Tracker issue"},
)
def update(
    key: IssueKey, body: IssueUpdate, client: TrackerClient = Depends(tracker_client)
) -> Issue:
    """Update fields of a Tracker issue; only the keys present in ``body`` are changed.

    Status is NOT changed here — use ``transitions_execute``. Returns the updated issue.
    """
    return client.issues.update(key, body)


@mcp.tool(name="issues_move", annotations={**WRITE, "title": "Move Tracker issue"})
def move(
    key: IssueKey,
    queue: Annotated[str, Field(description="Target queue key, e.g. NEW.")],
    expand: Expand = None,
    initial_status: Annotated[
        bool | None,
        Field(description="Reset the status to the new queue's initial one."),
    ] = None,
    move_all_fields: Annotated[
        bool | None,
        Field(description="Keep the versions, components and projects the new queue also has."),
    ] = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Issue:
    """Move a Tracker issue to another queue (it gets a new key there; the old key redirects).

    ``queue`` is the target queue key. Fields that do not exist in the target queue may be
    dropped. Returns the moved issue with its new key.
    """
    return client.issues.move(
        key,
        queue,
        expand=expand,
        initial_status=initial_status,
        move_all_fields=move_all_fields,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="issues_scroll_clear",
    annotations={**WRITE_IDEMPOTENT, "title": "Clear Tracker search scroll"},
)
def scroll_clear(body: ScrollClear, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Release the server resources of a scrolled issue search (harmless housekeeping).

    ``body`` maps each ``X-Scroll-Id`` to its ``X-Scroll-Token`` from a scrolled
    ``issues.search`` response. Returns an acknowledgement on success.
    """
    client.issues.scroll_clear(body)
    return Ack.cleared("search scroll resources")


@mcp.tool(
    name="issues_update_bulk",
    annotations={**WRITE, "title": "Bulk-update Tracker issues"},
)
def update_bulk(
    body: BulkUpdate, notify: Notify = None, client: TrackerClient = Depends(tracker_client)
) -> BulkChange:
    """Start an async bulk field update over many Tracker issues; returns the operation.

    Poll the returned operation id with ``bulk_get`` and inspect failures with
    ``bulk_issues_list``.
    """
    return client.issues.update_bulk(body, notify=notify)


@mcp.tool(name="issues_move_bulk", annotations={**WRITE, "title": "Bulk-move Tracker issues"})
def move_bulk(
    body: BulkMove, notify: Notify = None, client: TrackerClient = Depends(tracker_client)
) -> BulkChange:
    """Start an async bulk move of many Tracker issues to another queue; returns the operation.

    Poll with ``bulk_get``.
    """
    return client.issues.move_bulk(body, notify=notify)


@mcp.tool(
    name="issues_transition_bulk",
    annotations={**WRITE, "title": "Bulk-transition Tracker issues"},
)
def transition_bulk(
    body: BulkTransition, notify: Notify = None, client: TrackerClient = Depends(tracker_client)
) -> BulkChange:
    """Start an async bulk status transition over many Tracker issues; returns the operation.

    Poll with ``bulk_get``.
    """
    return client.issues.transition_bulk(body, notify=notify)


@mcp.tool(name="issues_import", annotations={**WRITE, "title": "Import Tracker issue"})
def import_(body: ImportTask, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """Import an issue preserving its original history (admin-only back-fill).

    Returns the imported issue.
    """
    return client.issues.import_(body=body)
