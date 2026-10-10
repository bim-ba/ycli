"""`tracker triggers` commands."""

import json
from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, NextOption
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.triggers.models import (
    Trigger,
    TriggerCreate,
    TriggerUpdate,
    WebhookLogEntry,
)
from ycli.yandex.tracker.typedefs import QueueIDArg

app = typer.Typer(name="triggers", help="Tracker queue triggers.", no_args_is_help=True)

TriggerIDArg = Annotated[
    int, typer.Argument(metavar="TRIGGER_ID", help="Numeric trigger identifier.")
]
TriggerActionOpt = Annotated[
    list[str] | None,
    typer.Option("--action", help="Trigger action as a JSON object (repeatable)."),
]
ConditionOpt = Annotated[
    list[str] | None,
    typer.Option("--condition", help="Trigger condition as a JSON object (repeatable)."),
]


@app.command("list")
def list_(
    queue_id: QueueIDArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> Listing[Trigger]:
    """List the triggers of QUEUE_ID (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.triggers.list(queue_id, limit=cap, next=next_)


@app.command()
def get(queue_id: QueueIDArg, trigger_id: TriggerIDArg, *, tracker: TrackerClient) -> Trigger:
    """Get trigger TRIGGER_ID of QUEUE_ID."""
    return tracker.triggers.get(queue_id, trigger_id)


@app.command()
def create(
    queue_id: QueueIDArg,
    name: Annotated[str, typer.Option(help="Name of the new trigger.")],
    action: TriggerActionOpt = None,
    condition: ConditionOpt = None,
    active: Annotated[
        bool | None, typer.Option("--active/--inactive", help="Start active or disabled.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Trigger:
    """Create a trigger on QUEUE_ID (POST /queues/{queue_id}/triggers).

    Pass one or more --action JSON objects (and optional --condition JSON objects), e.g.
    --action '{"type": "Transition", "status": {"key": "open"}}'.
    """
    body = TriggerCreate(
        name=name,
        actions=[json.loads(a) for a in action] if action else [],
        conditions=[json.loads(c) for c in condition] if condition else None,
        active=active,
    )
    return tracker.triggers.create(queue_id, body)


@app.command()
def update(
    queue_id: QueueIDArg,
    trigger_id: TriggerIDArg,
    name: Annotated[str | None, typer.Option(help="New name of the trigger.")] = None,
    action: TriggerActionOpt = None,
    condition: ConditionOpt = None,
    active: Annotated[
        bool | None, typer.Option("--active/--inactive", help="Activate or disable the trigger.")
    ] = None,
    version: Annotated[
        int | None, typer.Option(help="Current trigger version (optimistic lock).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Trigger:
    """Edit trigger TRIGGER_ID of QUEUE_ID (PATCH ...?version=) — only supplied fields are sent."""
    body = TriggerUpdate(
        name=name,
        actions=[json.loads(a) for a in action] if action else None,
        conditions=[json.loads(c) for c in condition] if condition else None,
        active=active,
    )
    return tracker.triggers.update(queue_id, trigger_id, body, version=version)


@app.command("webhook-log-list")
def webhook_log_list(
    queue_id: QueueIDArg,
    trigger_id: TriggerIDArg,
    issue_id: Annotated[
        str | None, typer.Option("--issue-id", help="Scope the logs to one issue key/id.")
    ] = None,
    limit: Annotated[
        int | None, typer.Option(help="Max records (API default 10, max 100).")
    ] = None,
    date_from: Annotated[
        str | None, typer.Option(help="Range start (YYYY-MM-DDThh:mm:ss.sss±hhmm).")
    ] = None,
    date_to: Annotated[
        str | None, typer.Option(help="Range end (YYYY-MM-DDThh:mm:ss.sss±hhmm).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[WebhookLogEntry]:
    """List the HTTP-action (Webhook) run logs of trigger TRIGGER_ID."""
    return tracker.triggers.webhook_log_list(
        queue_id,
        trigger_id,
        issue_id=issue_id,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
    )
