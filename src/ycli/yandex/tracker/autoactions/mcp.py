"""Tracker queue autoactions FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.autoactions.models import (
    Autoaction,
    AutoactionCreate,
    AutoactionLogList,
    AutoactionRunList,
)
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, WRITE, WRITE_TAGS, tracker_client

mcp = FastMCP("tracker-autoactions")


@mcp.tool(
    name="autoactions_get", annotations={**RO, "title": "Get Tracker queue autoaction"}, tags=TAGS
)
def get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DESIGN) or numeric queue id.")
    ],
    action_id: Annotated[int, Field(description="Numeric identifier of the autoaction.")],
    client: TrackerClient = Depends(tracker_client),
) -> Autoaction:
    """One queue autoaction by id — its filter/query, actions, schedule and run stats.

    An autoaction periodically applies its actions to every issue matching its filter/query.
    For run history use ``autoactions_logs_list`` (summaries) then ``autoactions_logs_get``
    (per-issue outcomes of one run).

    Example:
        >>> autoactions_get("DESIGN", 9)  # doctest: +SKIP
    """
    return client.autoactions.get(queue_id, action_id)


@mcp.tool(
    name="autoactions_logs_list",
    annotations={**RO, "title": "List Tracker autoaction runs"},
    tags=TAGS,
)
def logs_list(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DESIGN) or numeric queue id.")
    ],
    action_id: Annotated[int, Field(description="Numeric identifier of the autoaction.")],
    client: TrackerClient = Depends(tracker_client),
) -> AutoactionLogList:
    """Run summaries for an autoaction — one record per launch with hit/success/failure counts.

    Each record's ``id`` is the run id you pass to ``autoactions_logs_get`` for that run's
    per-issue outcomes.

    Example:
        >>> autoactions_logs_list("DESIGN", 9)  # doctest: +SKIP
    """
    return client.autoactions.logs(queue_id, action_id)


@mcp.tool(
    name="autoactions_logs_get",
    annotations={**RO, "title": "Get Tracker autoaction run"},
    tags=TAGS,
)
def logs_get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DESIGN) or numeric queue id.")
    ],
    action_id: Annotated[int, Field(description="Numeric identifier of the autoaction.")],
    run_id: Annotated[str, Field(description="Identifier of the autoaction run (from logs_list).")],
    client: TrackerClient = Depends(tracker_client),
) -> AutoactionRunList:
    """The per-issue outcomes of one autoaction run — each issue touched and its result status.

    Get the ``run_id`` from ``autoactions_logs_list``. Only autoactions that auto-update issues
    produce these detail logs.

    Example:
        >>> autoactions_logs_get("DESIGN", 9, "6819cc43")  # doctest: +SKIP
    """
    return client.autoactions.log_detail(queue_id, action_id, run_id)


@mcp.tool(
    name="autoactions_create",
    annotations={**WRITE, "title": "Create Tracker queue autoaction"},
    tags=WRITE_TAGS,
)
def create(
    queue_id: str, body: AutoactionCreate, client: TrackerClient = Depends(tracker_client)
) -> Autoaction:
    """Create an autoaction on a queue — actions applied on a schedule to matching issues.

    Required: ``name`` and ``actions`` (e.g. ``[{"type": "Update", …}]``); scope the issues
    with ``filter`` or ``query`` and set the cadence via ``intervalMillis`` / ``calendar``.
    CAUTION: autoactions have no delete endpoint — the action persists until its queue is
    deleted (it can be disabled in the UI).
    """
    return client.autoactions.create(queue_id, body)
