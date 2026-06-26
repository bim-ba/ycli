"""`tracker priorities` commands."""
from __future__ import annotations

import typer

from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="priorities", help="Tracker priorities.", no_args_is_help=True)


@app.callback()
def _callback() -> None:
    """Tracker priorities."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all priorities."""
    print(tracker_client(ctx).priorities.list().model_dump_json(by_alias=True))
