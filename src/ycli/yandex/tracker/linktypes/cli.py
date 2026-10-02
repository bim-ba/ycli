"""`tracker linktypes` commands."""

from __future__ import annotations

import typer

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.linktypes.models import LinkTypeList

app = typer.Typer(name="linktypes", help="Tracker link types.", no_args_is_help=True)


@app.command("list")
def list_(*, tracker: TrackerClient) -> LinkTypeList:
    """List all link types."""
    return tracker.linktypes.list()
