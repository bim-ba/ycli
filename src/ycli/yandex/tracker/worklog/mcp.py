"""Tracker worklog FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    IssueKey,
    WorklogRecordID,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.worklog.models import (
    ImportWorklog,
    Worklog,
    WorklogCreate,
    WorklogSearch,
    WorklogUpdate,
)

mcp = FastMCP("tracker-worklog")


@mcp.tool(name="worklog_list", annotations={**RO, "title": "List Tracker worklog"})
def list_(
    key: IssueKey,
    limit: Annotated[
        int | None,
        Field(ge=1, description=f"Max records to return; {LIMIT_CAP}"),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Worklog]:
    """All time-tracking entries logged against a single Tracker issue.

    Auto-paginated via the relative id-cursor. Capped at the configured item cap unless ``limit``
    is given.

    Scoped to one issue by ``key``. To search worklog across the whole org (by author and/or a
    creation-time range) use ``worklog_search`` instead.
    """
    cap = config.http.cap(limit)
    return client.worklog.list(key, limit=cap)


@mcp.tool(name="worklog_search", annotations={**RO, "title": "Search Tracker worklog"})
def search(
    created_by: Annotated[
        str | None, Field(description="Login or id of the record author to filter by.")
    ] = None,
    created_from: Annotated[
        str | None, Field(description="Start of the creation-time range (``YYYY-MM-DDThh:mm:ss``).")
    ] = None,
    created_to: Annotated[
        str | None, Field(description="End of the creation-time range (``YYYY-MM-DDThh:mm:ss``).")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Worklog]:
    """Org-wide worklog entries filtered by author and/or a creation-time range.

    Unlike ``worklog_list`` (one issue), this searches every issue's worklog. Pass
    ``created_by`` to scope to a user and ``created_from`` / ``created_to`` for a time window;
    all are optional.
    """
    period = {"from": created_from, "to": created_to}
    given = created_from is not None or created_to is not None
    body = WorklogSearch.model_validate(
        {"createdBy": created_by, "createdAt": period if given else None}
    )
    return client.worklog.search(body)


@mcp.tool(
    name="worklog_list_global",
    annotations={**RO, "title": "List Tracker org-wide worklog"},
)
def list_global(
    created_by: Annotated[
        str | None, Field(description="Login or id of the record author to filter by.")
    ] = None,
    created_at: Annotated[
        str | None, Field(description="Creation timestamp to filter by (``YYYY-MM-DDThh:mm:ss``).")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Worklog]:
    """Org-wide worklog entries via ``GET /worklog`` query filters (author / exact timestamp).

    A lighter sibling of ``worklog_search`` (which takes a time *range*); both filters are
    optional.
    """
    return client.worklog.list_global(created_by=created_by, created_at=created_at)


@mcp.tool(
    name="worklog_create",
    annotations={**WRITE, "title": "Add Tracker worklog record"},
)
def create(
    key: IssueKey, body: WorklogCreate, client: TrackerClient = Depends(tracker_client)
) -> Worklog:
    """Log spent time on a Tracker issue; returns the created worklog record."""
    return client.worklog.create(key, body)


@mcp.tool(
    name="worklog_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker worklog record"},
)
def update(
    key: IssueKey,
    record_id: WorklogRecordID,
    body: WorklogUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Worklog:
    """Edit a worklog record on a Tracker issue (duration and/or comment).

    Get ``record_id`` from ``worklog_list``. Returns the updated record.
    """
    return client.worklog.update(key, record_id, body)


@mcp.tool(
    name="worklog_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker worklog record"},
)
def delete(
    key: IssueKey, record_id: WorklogRecordID, client: TrackerClient = Depends(tracker_client)
) -> Ack:
    """Permanently delete a worklog record from a Tracker issue (irreversible).

    Get ``record_id`` from ``worklog_list``. Returns an acknowledgement on success.
    """
    client.worklog.delete(key, record_id)
    return Ack.deleted("worklog", record_id, on=key)


@mcp.tool(
    name="worklog_import",
    annotations={**WRITE, "title": "Import Tracker worklog record"},
)
def import_(
    issue_key: IssueKey, body: ImportWorklog, client: TrackerClient = Depends(tracker_client)
) -> ItemList[Worklog]:
    """Import a worklog record preserving its original author and timestamps (admin-only).

    Returns the imported record(s) — the endpoint answers with a JSON array.
    """
    return client.worklog.import_(issue_key, body=body)
