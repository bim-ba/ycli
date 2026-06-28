"""`tracker priorities` commands."""
from __future__ import annotations

import typer

from ycli.cliformat import output_format
from ycli.output import render

from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="priorities", help="Tracker priorities.", no_args_is_help=True)


@app.callback()
def _callback() -> None:
    """Tracker priorities."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all priorities."""
    render(tracker_client(ctx).priorities.list(), output_format=output_format(ctx))
