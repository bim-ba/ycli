"""Tracker queue triggers FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.triggers.models import Trigger, WebhookLogList

mcp = FastMCP("tracker-triggers")


@mcp.tool(name="triggers_get", annotations={**RO, "title": "Get Tracker queue trigger"}, tags=TAGS)
def get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DESIGN) or numeric queue id.")
    ],
    trigger_id: Annotated[int, Field(description="Numeric identifier of the trigger.")],
    client: TrackerClient = Depends(tracker_client),
) -> Trigger:
    """One queue trigger by id — its actions, firing conditions, order and active flag.

    Triggers run actions on an issue when their conditions match. Creating/editing triggers is
    a write (CLI/SDK only); the webhook-action run log is ``triggers_webhooklog_list``.

    Example:
        >>> triggers_get("DESIGN", 16)  # doctest: +SKIP
    """
    return client.triggers.get(queue_id, trigger_id)


@mcp.tool(
    name="triggers_webhooklog_list",
    annotations={**RO, "title": "List Tracker trigger webhook logs"},
    tags=TAGS,
)
def webhooklog_list(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DEV) or numeric queue id.")
    ],
    trigger_id: Annotated[int, Field(description="Numeric identifier of the trigger.")],
    issue_id: Annotated[
        str, Field(description="Optional issue key/id to scope the logs to one issue.")
    ] = "",
    limit: Annotated[
        int, Field(description="Max records (API default 10, max 100); 0 uses the API default.")
    ] = 0,
    client: TrackerClient = Depends(tracker_client),
) -> WebhookLogList:
    """The execution log of a trigger's HTTP-request (Webhook) action, newest first.

    Each record holds the outbound request and received response for one run. Only Webhook
    actions produce these; a trigger with no HTTP action returns an empty list.

    Example:
        >>> triggers_webhooklog_list("DEV", 6, limit=100)  # doctest: +SKIP
    """
    return client.triggers.webhook_log(
        queue_id, trigger_id, issue_id=issue_id or None, limit=limit or None
    )
