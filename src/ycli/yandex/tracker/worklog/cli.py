"""`tracker worklog` commands."""

from __future__ import annotations

import typer

from ycli.context import AppContext
from ycli.output import Serializer
from ycli.yandex.tracker._types import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="worklog", help="Tracker issue worklog.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List worklog entries for issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.worklog.list(key), app_ctx.strategy, app_ctx.console)
