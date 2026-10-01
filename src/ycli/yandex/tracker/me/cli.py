"""`tracker me` commands."""

from __future__ import annotations

import typer

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.me.models import Me

app = typer.Typer(name="me", help="Tracker authenticated user.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(*, tracker: TrackerClient) -> Me:
    """Print the authenticated user (a safe auth probe)."""
    return tracker.me.get()
