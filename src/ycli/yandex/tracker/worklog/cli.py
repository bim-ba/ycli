"""`tracker worklog` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.context import AppContext
from ycli.output import Serializer

app = typer.Typer(name="worklog", help="Tracker issue worklog.", no_args_is_help=True)


@app.callback()
def _callback() -> None:
    """Tracker issue worklog."""


@app.command("list")
def list_(ctx: typer.Context, key: Annotated[str, typer.Argument(metavar="KEY", help="Issue key.")]) -> None:
    """List worklog entries for issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.worklog.list(key), app_ctx.strategy, app_ctx.console)
