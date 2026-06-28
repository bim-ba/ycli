"""`tracker changelog` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.context import AppContext
from ycli.output import Serializer

app = typer.Typer(name="changelog", help="Tracker issue changelog.", no_args_is_help=True)


@app.callback()
def _callback() -> None:
    """Tracker issue changelog."""


@app.command("list")
def list_(
    ctx: typer.Context,
    key: Annotated[str, typer.Argument(metavar="KEY", help="Issue key.")],
    per_page: Annotated[int, typer.Option("--per-page", help="Entries per page.")] = 100,
) -> None:
    """List changelog entries for issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.changelog.list(key, per_page=per_page), app_ctx.strategy, app_ctx.console)
