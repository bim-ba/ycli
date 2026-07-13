"""Tracker bulk-change FastMCP tools (reads + writes, ARCH-3 honest annotations).

The bulk *triggers* (update/move/transition) start an async operation and return its id;
the two reads observe it: fetch its status and list the issues it failed on.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.bulk.models import (
    BulkChange,
    BulkIssueResultList,
    BulkMove,
    BulkTransition,
    BulkUpdate,
)
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)

mcp = FastMCP("tracker-bulk")


@mcp.tool(name="bulk_get", annotations={**RO, "title": "Get Tracker bulk-change status"}, tags=TAGS)
def get(
    bulk_id: Annotated[
        str, Field(description="Bulk-change operation id, e.g. ``1ab23cd4e5678901``.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> BulkChange:
    """Current status of an async bulk-change operation (update/move/transition).

    ``status`` runs ``CREATED`` → ``COMPLETE`` / ``FAILED``; ``totalIssues`` /
    ``totalCompletedIssues`` show progress. Poll this after a bulk trigger returns an id;
    once it reports ``FAILED``, call ``bulk_issues_list`` for the per-issue errors.

    Example:
        >>> get(bulk_id="1ab23cd4e5678901")  # doctest: +SKIP
    """
    return client.bulk.get(bulk_id)


@mcp.tool(
    name="bulk_issues_list",
    annotations={**RO, "title": "List Tracker bulk-change failed issues"},
    tags=TAGS,
)
def issues_list(
    bulk_id: Annotated[str, Field(description="Bulk-change operation id to inspect.")],
    client: TrackerClient = Depends(tracker_client),
) -> BulkIssueResultList:
    """The issues a bulk-change operation could NOT change, each with its per-field error.

    Use after ``bulk_get`` reports a non-zero failure count to see *why* specific issues were
    rejected (e.g. an invalid resolution for the target queue/type). Successful issues are not
    listed here.

    Example:
        >>> issues_list(bulk_id="1ab23cd4e5678901")  # doctest: +SKIP
    """
    return client.bulk.issues(bulk_id)


@mcp.tool(
    name="bulk_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Bulk-update Tracker issues"},
    tags=WRITE_TAGS,
)
def update(body: BulkUpdate, client: TrackerClient = Depends(tracker_client)) -> BulkChange:
    """Start an async bulk field update over many Tracker issues; returns the operation.

    Poll the returned operation id with ``bulk_get`` and inspect failures with
    ``bulk_issues_list``.
    """
    return client.bulk.update(body.model_dump(by_alias=True, exclude_none=True))


@mcp.tool(
    name="bulk_move", annotations={**WRITE, "title": "Bulk-move Tracker issues"}, tags=WRITE_TAGS
)
def move(body: BulkMove, client: TrackerClient = Depends(tracker_client)) -> BulkChange:
    """Start an async bulk move of many Tracker issues to another queue; returns the operation.

    Poll with ``bulk_get``.
    """
    return client.bulk.move(body.model_dump(by_alias=True, exclude_none=True))


@mcp.tool(
    name="bulk_transition",
    annotations={**WRITE, "title": "Bulk-transition Tracker issues"},
    tags=WRITE_TAGS,
)
def transition(body: BulkTransition, client: TrackerClient = Depends(tracker_client)) -> BulkChange:
    """Start an async bulk status transition over many Tracker issues; returns the operation.

    Poll with ``bulk_get``.
    """
    return client.bulk.transition(body.model_dump(by_alias=True, exclude_none=True))
