"""`forms me` commands."""

from __future__ import annotations

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.me.models import User

app = typer.Typer(name="me", help="Forms authenticated user.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(*, forms: FormsClient) -> User:
    """Print the authenticated user (a safe auth probe)."""
    return forms.me.get()
