"""Tracker worklog FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.worklog.models import Worklog, WorklogList

mcp = FastMCP("tracker-worklog")


@mcp.tool(name="worklog_list", annotations={**RO, "title": "List Tracker worklog"}, tags=TAGS)
def list_(
    key: str,
    limit: Annotated[
        int,
        Field(description="Max records to return; 0 means the YCLI_MAX_ITEMS cap (default 500)."),
    ] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> WorklogList:
    """All time-tracking entries logged against a single Tracker issue, auto-paginated via the
    relative id-cursor. Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given.

    Scoped to one issue by ``key``. To search worklog across the whole org (by author and/or a
    creation-time range) use ``worklog_search`` instead.

    Example:
        >>> list_(key="QUEUE-123")  # doctest: +SKIP
    """
    cap = resolve_cap(limit, config.max_items)
    return client.worklog.list(key, limit=cap)


@mcp.tool(name="worklog_search", annotations={**RO, "title": "Search Tracker worklog"}, tags=TAGS)
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
) -> WorklogList:
    """Org-wide worklog entries filtered by author and/or a creation-time range.

    Unlike ``worklog_list`` (one issue), this searches every issue's worklog. Pass
    ``created_by`` to scope to a user and ``created_from`` / ``created_to`` for a time window;
    all are optional.

    Example:
        >>> search(created_by="veikus", created_from="2018-06-06T00:00:00")  # doctest: +SKIP
    """
    body: dict[str, object] = {}
    if created_by:
        body["createdBy"] = created_by
    created_at = {k: v for k, v in (("from", created_from), ("to", created_to)) if v}
    if created_at:
        body["createdAt"] = created_at
    return client.worklog.search(body)


@mcp.tool(
    name="worklog_global_list",
    annotations={**RO, "title": "List Tracker org-wide worklog"},
    tags=TAGS,
)
def global_list(
    created_by: Annotated[
        str | None, Field(description="Login or id of the record author to filter by.")
    ] = None,
    created_at: Annotated[
        str | None, Field(description="Creation timestamp to filter by (``YYYY-MM-DDThh:mm:ss``).")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> WorklogList:
    """Org-wide worklog entries via ``GET /worklog`` query filters (author / exact timestamp).

    A lighter sibling of ``worklog_search`` (which takes a time *range*); both filters are
    optional.
    """
    return client.worklog.global_list(created_by=created_by, created_at=created_at)


@mcp.tool(
    name="worklog_create",
    annotations={**WRITE, "title": "Add Tracker worklog record"},
    tags=WRITE_TAGS,
)
def create(key: str, body: dict, client: TrackerClient = Depends(tracker_client)) -> Worklog:
    """Log spent time on a Tracker issue; returns the created worklog record.

    ``body`` is the raw API payload — required ``{"start": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
    "duration": "PT2H"}`` (ISO-8601 duration); optional ``comment``.
    """
    return client.worklog.create(key, body)


@mcp.tool(
    name="worklog_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker worklog record"},
    tags=WRITE_TAGS,
)
def edit(
    key: str, record_id: str, body: dict, client: TrackerClient = Depends(tracker_client)
) -> Worklog:
    """Edit a worklog record on a Tracker issue (duration and/or comment).

    Get ``record_id`` from ``worklog_list``. ``body`` carries the fields to change, e.g.
    ``{"duration": "PT1H30M"}``. Returns the updated record.
    """
    return client.worklog.edit(key, record_id, body)


@mcp.tool(
    name="worklog_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker worklog record"},
    tags=WRITE_TAGS,
)
def delete(key: str, record_id: str, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete a worklog record from a Tracker issue (irreversible).

    Get ``record_id`` from ``worklog_list``. Returns an acknowledgement on success.
    """
    client.worklog.delete(key, record_id)
    return Ack(detail=f"deleted worklog record {record_id} on {key}")
