"""`wiki me` commands."""

from __future__ import annotations

import typer

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.me.models import Me

app = typer.Typer(name="me", help="Wiki authenticated user.", no_args_is_help=True)


@app.command()
def get(*, wiki: WikiClient) -> Me:
    """Print the authenticated user (a safe auth probe)."""
    return wiki.me.get()
