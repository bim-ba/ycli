"""`tracker applications` commands."""

from __future__ import annotations

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="applications", help="Tracker external applications.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List external applications that issues can be linked to."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.applications.list(), app_ctx.strategy, app_ctx.console)
