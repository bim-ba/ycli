"""`tracker fields` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="fields", help="Tracker global fields.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all global fields of the organisation."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.fields.list(), app_ctx.strategy, app_ctx.console)


@app.command()
def get(
    ctx: typer.Context,
    field_id: Annotated[
        str, typer.Argument(metavar="FIELD_ID", help="Identifier of the issue field.")
    ],
) -> None:
    """Get parameters of one issue field by FIELD_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.fields.get(field_id=field_id), app_ctx.strategy, app_ctx.console
    )
