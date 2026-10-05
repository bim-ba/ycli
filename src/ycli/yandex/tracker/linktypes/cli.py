"""`tracker linktypes` commands."""

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.models import LinkType

app = typer.Typer(name="linktypes", help="Tracker link types.", no_args_is_help=True)


@app.command("list")
def list_(*, tracker: TrackerClient) -> ItemList[LinkType]:
    """List all link types."""
    return tracker.linktypes.list()
