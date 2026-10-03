"""`tracker autoactions` commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.cli.aliases import deprecated_alias
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.autoactions.models import (
    Autoaction,
    AutoactionCalendar,
    AutoactionCreate,
    AutoactionLogEntry,
    AutoactionRunEntry,
)
from ycli.yandex.tracker.client import TrackerClient

app = typer.Typer(name="autoactions", help="Tracker queue autoactions.", no_args_is_help=True)

QueueIdArg = Annotated[
    str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
]
ActionIdArg = Annotated[
    int, typer.Argument(metavar="ACTION_ID", help="Numeric autoaction identifier.")
]


@app.command()
def get(queue_id: QueueIdArg, action_id: ActionIdArg, *, tracker: TrackerClient) -> Autoaction:
    """Get autoaction ACTION_ID of QUEUE_ID."""
    return tracker.autoactions.get(queue_id, action_id)


@app.command()
def create(
    queue_id: QueueIdArg,
    name: Annotated[str, typer.Option(help="Name of the new autoaction.")],
    query: Annotated[str, typer.Option(help="TQL query selecting the issues to act on.")] = "",
    filter_: Annotated[
        str, typer.Option("--filter", help="Field-based filter as a JSON object.")
    ] = "",
    action: Annotated[
        list[str] | None,
        typer.Option("--action", help="Autoaction action as a JSON object (repeatable)."),
    ] = None,
    active: Annotated[
        bool | None, typer.Option("--active/--inactive", help="Start active or disabled.")
    ] = None,
    enable_notifications: Annotated[
        bool | None,
        typer.Option("--notify/--no-notify", help="Send notifications when the autoaction runs."),
    ] = None,
    interval_millis: Annotated[
        int, typer.Option("--interval-millis", help="Run interval in ms (default 3600000).")
    ] = 0,
    calendar_id: Annotated[
        int, typer.Option("--calendar-id", help="Working-calendar id for the active window.")
    ] = 0,
    *,
    tracker: TrackerClient,
) -> Autoaction:
    """Create an autoaction on QUEUE_ID (POST /queues/{queue_id}/autoactions).

    Supply --query or --filter to select issues, and one or more --action JSON objects, e.g.
    --action '{"type": "Transition", "status": {"key": "needInfo"}}'.
    """
    body = AutoactionCreate(
        name=name,
        query=query or None,
        filter=json.loads(filter_) if filter_ else None,
        actions=[json.loads(a) for a in action] if action else [],
        active=active,
        enable_notifications=enable_notifications,
        interval_millis=interval_millis or None,
        calendar=AutoactionCalendar(id=calendar_id) if calendar_id else None,
    )
    return tracker.autoactions.create(queue_id, body)


@deprecated_alias(app, "logs")
@app.command()
def logs_list(
    queue_id: QueueIdArg, action_id: ActionIdArg, *, tracker: TrackerClient
) -> ItemList[AutoactionLogEntry]:
    """List the run summaries of autoaction ACTION_ID."""
    return tracker.autoactions.logs(queue_id, action_id)


@deprecated_alias(app, "log-detail")
@app.command("logs-get")
def logs_get(
    queue_id: QueueIdArg,
    action_id: ActionIdArg,
    run_id: Annotated[str, typer.Argument(metavar="RUN_ID", help="Autoaction run identifier.")],
    *,
    tracker: TrackerClient,
) -> ItemList[AutoactionRunEntry]:
    """List the per-issue outcomes of run RUN_ID of autoaction ACTION_ID."""
    return tracker.autoactions.log_detail(queue_id, action_id, run_id)
