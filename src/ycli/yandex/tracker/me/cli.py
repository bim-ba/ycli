"""`tracker me` commands."""
from __future__ import annotations

import typer

from ycli.output import render
from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="me", help="Tracker authenticated user.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(ctx: typer.Context) -> None:
    """Print the authenticated user (a safe auth probe)."""
    render(tracker_client(ctx).me.get())
