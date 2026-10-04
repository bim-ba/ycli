"""`tracker macros` commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.macros.models import Macro, MacroCreate, MacroUpdate
from ycli.yandex.tracker.typedefs import QueueIDArg

app = typer.Typer(name="macros", help="Tracker queue macros.", no_args_is_help=True)

MacroIDArg = Annotated[int, typer.Argument(metavar="MACRO_ID", help="Numeric macro identifier.")]


@app.command("list")
def list_(queue_id: QueueIDArg, *, tracker: TrackerClient) -> ItemList[Macro]:
    """List the macros of QUEUE_ID."""
    return tracker.macros.list(queue_id)


@app.command()
def get(queue_id: QueueIDArg, macro_id: MacroIDArg, *, tracker: TrackerClient) -> Macro:
    """Get macro MACRO_ID of QUEUE_ID."""
    return tracker.macros.get(queue_id, macro_id)


@app.command()
def create(
    queue_id: QueueIDArg,
    name: Annotated[str, typer.Option(help="Name of the new macro.")],
    body: Annotated[
        str | None, typer.Option(help="Comment text created when the macro runs.")
    ] = None,
    issue_update: Annotated[
        str | None,
        typer.Option("--issue-update", help="Field→value issue changes as a JSON object."),
    ] = None,
    *,
    tracker: TrackerClient,
) -> Macro:
    """Create a macro on QUEUE_ID (POST /queues/{queue_id}/macros)."""
    macro = MacroCreate(
        name=name,
        body=body,
        issue_update=json.loads(issue_update) if issue_update is not None else None,
    )
    return tracker.macros.create(queue_id, macro)


@app.command()
def update(
    queue_id: QueueIDArg,
    macro_id: MacroIDArg,
    name: Annotated[str | None, typer.Option(help="New name of the macro.")] = None,
    body: Annotated[
        str | None, typer.Option(help="New comment text created when the macro runs.")
    ] = None,
    issue_update: Annotated[
        str | None,
        typer.Option(
            "--issue-update", help="Replacement field→value issue changes as a JSON object."
        ),
    ] = None,
    *,
    tracker: TrackerClient,
) -> Macro:
    """Edit macro MACRO_ID of QUEUE_ID (PATCH) — only supplied fields are sent."""
    macro = MacroUpdate(
        name=name,
        body=body,
        issue_update=json.loads(issue_update) if issue_update is not None else None,
    )
    return tracker.macros.update(queue_id, macro_id, macro)


@app.command()
def delete(queue_id: QueueIDArg, macro_id: MacroIDArg, *, tracker: TrackerClient) -> Ack:
    """Delete macro MACRO_ID of QUEUE_ID (DELETE)."""
    tracker.macros.delete(queue_id, macro_id)
    return Ack.deleted("macro", macro_id, from_=f"queue {queue_id}")
