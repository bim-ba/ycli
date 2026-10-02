"""Tracker queue triggers FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    LIMIT_CAP,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    QueueId,
    Version,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.triggers.models import (
    Trigger,
    TriggerCreate,
    TriggerList,
    TriggerUpdate,
    WebhookLogList,
)

mcp = FastMCP("tracker-triggers")


@mcp.tool(
    name="triggers_list", annotations={**RO, "title": "List Tracker queue triggers"}, tags=TAGS
)
def list_(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DESIGN) or numeric queue id.")
    ],
    limit: Annotated[int, Field(description=f"Max triggers to return; {LIMIT_CAP}")] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> TriggerList:
    """Every trigger of a queue, ascending by id: name, actions, conditions and active flag.

    Auto-paginated and capped at the configured item cap unless ``limit`` is given. Use
    ``triggers_get`` for one trigger by id.

    Example:
        >>> triggers_list("DESIGN")  # doctest: +SKIP
    """
    cap = config.http.cap(limit)
    return client.triggers.list(queue_id, limit=cap)


@mcp.tool(name="triggers_get", annotations={**RO, "title": "Get Tracker queue trigger"}, tags=TAGS)
def get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DESIGN) or numeric queue id.")
    ],
    trigger_id: Annotated[int, Field(description="Numeric identifier of the trigger.")],
    client: TrackerClient = Depends(tracker_client),
) -> Trigger:
    """One queue trigger by id — its actions, firing conditions, order and active flag.

    Triggers run actions on an issue when their conditions match. The webhook-action run log is
    ``triggers_webhooklog_list``.

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


@mcp.tool(
    name="triggers_create",
    annotations={**WRITE, "title": "Create Tracker queue trigger"},
    tags=WRITE_TAGS,
)
def create(
    queue_id: QueueId,
    body: Annotated[
        TriggerCreate, Field(description="Trigger name, actions and optional conditions.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Trigger:
    """Create a trigger on a queue — actions that fire when an issue event matches conditions.

    Required: ``name`` and ``actions`` (e.g. ``[{"type": "Transition", …}]``); optional
    ``conditions`` scope when it fires. Returns the new trigger.
    """
    return client.triggers.create(queue_id, body)


@mcp.tool(
    name="triggers_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker queue trigger"},
    tags=WRITE_TAGS,
)
def edit(
    queue_id: QueueId,
    trigger_id: Annotated[int, Field(description="Numeric trigger id, from ``triggers_list``.")],
    body: Annotated[TriggerUpdate, Field(description="Fields to change; unset ones stay.")],
    version: Version = None,
    client: TrackerClient = Depends(tracker_client),
) -> Trigger:
    """Edit a queue trigger; only the fields set in ``body`` are changed.

    Get ``trigger_id`` from ``triggers_get`` / the queue settings. Pass ``version`` to guard
    against concurrent edits (optimistic locking).
    """
    return client.triggers.edit(queue_id, trigger_id, body, version=version)
