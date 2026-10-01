"""`tracker applications` commands."""

from __future__ import annotations

import typer

from ycli.yandex.tracker.applications.models import ApplicationList
from ycli.yandex.tracker.client import TrackerClient

app = typer.Typer(name="applications", help="Tracker external applications.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(*, tracker: TrackerClient) -> ApplicationList:
    """List external applications that issues can be linked to."""
    return tracker.applications.list()
