"""`tracker changelog` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.output import render

from ycli.yandex.tracker._clideps import tracker_client

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
    render(tracker_client(ctx).changelog.list(key, per_page=per_page))
