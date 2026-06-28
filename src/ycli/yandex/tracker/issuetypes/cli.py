"""`tracker issuetypes` commands."""
from __future__ import annotations

import typer

from ycli.context import AppContext
from ycli.output import Serializer

app = typer.Typer(name="issuetypes", help="Tracker issue types.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all issue types."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.issuetypes.list(), app_ctx.strategy, app_ctx.console)
