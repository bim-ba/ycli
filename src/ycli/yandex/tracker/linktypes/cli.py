"""`tracker linktypes` commands."""
from __future__ import annotations

import typer

from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="linktypes", help="Tracker link types.", no_args_is_help=True)


@app.callback()
def _callback() -> None:
    """Tracker link types."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all link types."""
    print(tracker_client(ctx).linktypes.list().model_dump_json(by_alias=True))
