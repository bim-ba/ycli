"""Tracker bulk-change FastMCP tools (reads-only).

The bulk *triggers* (update/move/transition) are writes and ship on the CLI/SDK only
(ARCH-3). Here the MCP surface exposes only the two reads an agent needs to *observe* a
running operation: fetch its status and list the issues it failed on.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.bulk.models import BulkChange, BulkIssueResultList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client

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
    ``totalCompletedIssues`` show progress. Poll this after a CLI bulk trigger returns an id;
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
