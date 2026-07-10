"""`tracker triggers` commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.triggers.models import TriggerCreate, TriggerUpdate

app = typer.Typer(name="triggers", help="Tracker queue triggers.", no_args_is_help=True)

QueueIdArg = Annotated[
    str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
]
TriggerIdArg = Annotated[
    int, typer.Argument(metavar="TRIGGER_ID", help="Numeric trigger identifier.")
]
ActionOpt = Annotated[
    list[str] | None,
    typer.Option("--action", help="Trigger action as a JSON object (repeatable)."),
]
ConditionOpt = Annotated[
    list[str] | None,
    typer.Option("--condition", help="Trigger condition as a JSON object (repeatable)."),
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(ctx: typer.Context, queue_id: QueueIdArg, trigger_id: TriggerIdArg) -> None:
    """Get trigger TRIGGER_ID of QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.triggers.get(queue_id, trigger_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def create(
    ctx: typer.Context,
    queue_id: QueueIdArg,
    name: Annotated[str, typer.Option(help="Name of the new trigger.")],
    action: ActionOpt = None,
    condition: ConditionOpt = None,
    active: Annotated[
        bool | None, typer.Option("--active/--inactive", help="Start active or disabled.")
    ] = None,
) -> None:
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
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.triggers.create(queue_id, body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def edit(
    ctx: typer.Context,
    queue_id: QueueIdArg,
    trigger_id: TriggerIdArg,
    name: Annotated[str, typer.Option(help="New name of the trigger.")] = "",
    action: ActionOpt = None,
    condition: ConditionOpt = None,
    active: Annotated[
        bool | None, typer.Option("--active/--inactive", help="Activate or disable the trigger.")
    ] = None,
    version: Annotated[int, typer.Option(help="Current trigger version (optimistic lock).")] = 0,
) -> None:
    """Edit trigger TRIGGER_ID of QUEUE_ID (PATCH ...?version=) — only supplied fields are sent."""
    body = TriggerUpdate(
        name=name or None,
        actions=[json.loads(a) for a in action] if action else None,
        conditions=[json.loads(c) for c in condition] if condition else None,
        active=active,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.triggers.edit(queue_id, trigger_id, body, version=version or None),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command("webhook-log")
def webhook_log(
    ctx: typer.Context,
    queue_id: QueueIdArg,
    trigger_id: TriggerIdArg,
    issue_id: Annotated[
        str, typer.Option("--issue-id", help="Scope the logs to one issue key/id.")
    ] = "",
    limit: Annotated[int, typer.Option(help="Max records (API default 10, max 100).")] = 0,
    date_from: Annotated[
        str, typer.Option("--from", help="Range start (YYYY-MM-DDThh:mm:ss.sss±hhmm).")
    ] = "",
    date_to: Annotated[
        str, typer.Option("--to", help="Range end (YYYY-MM-DDThh:mm:ss.sss±hhmm).")
    ] = "",
) -> None:
    """List the HTTP-action (Webhook) run logs of trigger TRIGGER_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.triggers.webhook_log(
            queue_id,
            trigger_id,
            issue_id=issue_id or None,
            limit=limit or None,
            date_from=date_from or None,
            date_to=date_to or None,
        ),
        app_ctx.strategy,
        app_ctx.console,
    )
