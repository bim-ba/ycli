"""`tracker me` commands."""

from __future__ import annotations

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="me", help="Tracker authenticated user.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(ctx: typer.Context) -> None:
    """Print the authenticated user (a safe auth probe)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.me.get(), app_ctx.strategy, app_ctx.console)
