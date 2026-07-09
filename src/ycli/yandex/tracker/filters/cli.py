"""`tracker filters` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="filters", help="Tracker saved filters.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(
    ctx: typer.Context,
    filter_id: Annotated[
        str, typer.Argument(metavar="FILTER_ID", help="Identifier of the saved filter.")
    ],
) -> None:
    """Get parameters of one saved filter by FILTER_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.filters.get(filter_id=filter_id), app_ctx.strategy, app_ctx.console
    )
