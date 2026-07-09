"""`tracker localfields` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="localfields", help="Tracker per-queue local fields.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    queue_id: Annotated[str, typer.Argument(help="Queue key (case-sensitive) or numeric id.")],
) -> None:
    """List the local fields of queue QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.localfields.list(queue_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def get(
    ctx: typer.Context,
    queue_id: Annotated[str, typer.Argument(help="Queue key (case-sensitive) or numeric id.")],
    field_key: Annotated[str, typer.Argument(help="Local field key (from `localfields list`).")],
) -> None:
    """Print one local field FIELD_KEY of queue QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.localfields.get(queue_id, field_key), app_ctx.strategy, app_ctx.console
    )
