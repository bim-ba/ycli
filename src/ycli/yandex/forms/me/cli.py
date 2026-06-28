"""`forms me` commands."""
from __future__ import annotations

import typer

from ycli.cliformat import output_format
from ycli.output import render

from ycli.yandex.forms._clideps import forms_client

app = typer.Typer(name="me", help="Forms authenticated user.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(ctx: typer.Context) -> None:
    """Print the authenticated user (a safe auth probe)."""
    render(forms_client(ctx).me.get(), output_format=output_format(ctx))
