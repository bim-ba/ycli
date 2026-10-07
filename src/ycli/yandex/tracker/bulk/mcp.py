"""Tracker bulk-change FastMCP tools: the status of a bulk change and what it failed on.

``issues_update_bulk``, ``issues_move_bulk`` and ``issues_transition_bulk`` start the
operation these two reads observe.
"""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.bulk.models import (
    BulkChange,
    BulkIssueResult,
)
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    new_server,
    tracker_client,
)

mcp = new_server("tracker-bulk")


@mcp.tool(name="bulk_get", annotations={**RO, "title": "Get Tracker bulk-change status"})
def get(
    bulk_id: Annotated[
        str, Field(description="Bulk-change operation id, e.g. ``1ab23cd4e5678901``.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> BulkChange:
    """Current status of an async bulk-change operation (``issues_update_bulk`` and its kin).

    ``status`` runs ``CREATED`` → ``COMPLETE`` / ``FAILED``; ``totalIssues`` /
    ``totalCompletedIssues`` show progress. Poll this after a bulk trigger returns an id;
    once it reports ``FAILED``, call ``bulk_issues_list`` for the per-issue errors.
    """
    return client.bulk.get(bulk_id)


@mcp.tool(
    name="bulk_issues_list",
    annotations={**RO, "title": "List the issues of a Tracker bulk change"},
)
def issues_list(
    bulk_id: Annotated[str, Field(description="Bulk-change operation id to inspect.")],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[BulkIssueResult]:
    """Every issue of a bulk change with how it went: its ``status`` and, when it failed, why.

    One record per issue, the ones that went well too (``COMPLETED``, measured). Use after
    ``bulk_get`` reports a failure to see which issues were rejected and why (e.g. an invalid
    resolution for the target queue/type): those carry ``error``.
    """
    return client.bulk.issues_list(bulk_id)
