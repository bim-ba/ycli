"""Tracker queue triggers FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    QueueID,
    Version,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.triggers.models import (
    Trigger,
    TriggerCreate,
    TriggerUpdate,
    WebhookLogEntry,
)

mcp = FastMCP("tracker-triggers")


@mcp.tool(name="triggers_list", annotations={**RO, "title": "List Tracker queue triggers"})
def list_(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DESIGN) or numeric queue id.")
    ],
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max triggers to return; {LIMIT_CAP}")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Trigger]:
    """Every trigger of a queue, ascending by id: name, actions, conditions and active flag.

    Auto-paginated and capped at the configured item cap unless ``limit`` is given. Use
    ``triggers_get`` for one trigger by id.
    """
    cap = config.http.cap(limit)
    return client.triggers.list(queue_id, limit=cap)


@mcp.tool(name="triggers_get", annotations={**RO, "title": "Get Tracker queue trigger"})
def get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DESIGN) or numeric queue id.")
    ],
    trigger_id: Annotated[int, Field(description="Numeric identifier of the trigger.")],
    client: TrackerClient = Depends(tracker_client),
) -> Trigger:
    """One queue trigger by id — its actions, firing conditions, order and active flag.

    Triggers run actions on an issue when their conditions match. The webhook-action run log is
    ``triggers_webhook_log_list``.
    """
    return client.triggers.get(queue_id, trigger_id)


@mcp.tool(
    name="triggers_webhook_log_list",
    annotations={**RO, "title": "List Tracker trigger webhook logs"},
)
def webhook_log_list(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. DEV) or numeric queue id.")
    ],
    trigger_id: Annotated[int, Field(description="Numeric identifier of the trigger.")],
    issue_id: Annotated[
        str | None, Field(description="Optional issue key/id to scope the logs to one issue.")
    ] = None,
    limit: Annotated[
        int | None,
        Field(description="Max records (the API's default is 10, its maximum 100)."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[WebhookLogEntry]:
    """The execution log of a trigger's HTTP-request (Webhook) action, newest first.

    Each record holds the outbound request and received response for one run. Only Webhook
    actions produce these; a trigger with no HTTP action returns an empty list.
    """
    return client.triggers.webhook_log_list(queue_id, trigger_id, issue_id=issue_id, limit=limit)


@mcp.tool(
    name="triggers_create",
    annotations={**WRITE, "title": "Create Tracker queue trigger"},
)
def create(
    queue_id: QueueID,
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
    name="triggers_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker queue trigger"},
)
def update(
    queue_id: QueueID,
    trigger_id: Annotated[int, Field(description="Numeric trigger id, from ``triggers_list``.")],
    body: Annotated[TriggerUpdate, Field(description="Fields to change; unset ones stay.")],
    version: Version = None,
    client: TrackerClient = Depends(tracker_client),
) -> Trigger:
    """Edit a queue trigger; only the fields set in ``body`` are changed.

    Get ``trigger_id`` from ``triggers_get`` / the queue settings. Pass ``version`` to guard
    against concurrent edits (optimistic locking).
    """
    return client.triggers.update(queue_id, trigger_id, body, version=version)
