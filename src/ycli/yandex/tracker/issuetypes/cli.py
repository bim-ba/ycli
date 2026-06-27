"""`tracker issuetypes` commands."""
from __future__ import annotations

import typer

from ycli.output import render

from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="issuetypes", help="Tracker issue types.", no_args_is_help=True)


@app.callback()
def _callback() -> None:
    """Tracker issue types."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all issue types."""
    render(tracker_client(ctx).issuetypes.list())
