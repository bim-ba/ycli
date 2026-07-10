"""`tracker macros` commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.macros.models import MacroCreate, MacroUpdate

app = typer.Typer(name="macros", help="Tracker queue macros.", no_args_is_help=True)

QueueIdArg = Annotated[
    str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
]
MacroIdArg = Annotated[int, typer.Argument(metavar="MACRO_ID", help="Numeric macro identifier.")]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context, queue_id: QueueIdArg) -> None:
    """List the macros of QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.macros.list(queue_id), app_ctx.strategy, app_ctx.console)


@app.command()
def get(ctx: typer.Context, queue_id: QueueIdArg, macro_id: MacroIdArg) -> None:
    """Get macro MACRO_ID of QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.macros.get(queue_id, macro_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def create(
    ctx: typer.Context,
    queue_id: QueueIdArg,
    name: Annotated[str, typer.Option(help="Name of the new macro.")],
    body: Annotated[str, typer.Option(help="Comment text created when the macro runs.")] = "",
    issue_update: Annotated[
        str,
        typer.Option("--issue-update", help="Field→value issue changes as a JSON object."),
    ] = "",
) -> None:
    """Create a macro on QUEUE_ID (POST /queues/{queue_id}/macros)."""
    macro = MacroCreate(
        name=name,
        body=body or None,
        issue_update=json.loads(issue_update) if issue_update else None,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.macros.create(queue_id, macro), app_ctx.strategy, app_ctx.console
    )


@app.command()
def edit(
    ctx: typer.Context,
    queue_id: QueueIdArg,
    macro_id: MacroIdArg,
    name: Annotated[str, typer.Option(help="New name of the macro.")] = "",
    body: Annotated[str, typer.Option(help="New comment text created when the macro runs.")] = "",
    issue_update: Annotated[
        str,
        typer.Option(
            "--issue-update", help="Replacement field→value issue changes as a JSON object."
        ),
    ] = "",
) -> None:
    """Edit macro MACRO_ID of QUEUE_ID (PATCH) — only supplied fields are sent."""
    macro = MacroUpdate(
        name=name or None,
        body=body or None,
        issue_update=json.loads(issue_update) if issue_update else None,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.macros.edit(queue_id, macro_id, macro), app_ctx.strategy, app_ctx.console
    )


@app.command()
def delete(ctx: typer.Context, queue_id: QueueIdArg, macro_id: MacroIdArg) -> None:
    """Delete macro MACRO_ID of QUEUE_ID (DELETE)."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.macros.delete(queue_id, macro_id)
    print(f"Deleted macro {macro_id} from queue {queue_id}")
