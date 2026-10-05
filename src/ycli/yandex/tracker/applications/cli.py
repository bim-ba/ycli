"""`tracker applications` commands."""

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.applications.models import Application
from ycli.yandex.tracker.client import TrackerClient

app = typer.Typer(name="applications", help="Tracker external applications.", no_args_is_help=True)


@app.command("list")
def list_(*, tracker: TrackerClient) -> ItemList[Application]:
    """List external applications that issues can be linked to."""
    return tracker.applications.list()
