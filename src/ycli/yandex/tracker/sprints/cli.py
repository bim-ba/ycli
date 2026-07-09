"""`tracker sprints` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="sprints", help="Tracker board sprints.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    board_id: Annotated[int, typer.Argument(metavar="BOARD_ID", help="Numeric board identifier.")],
) -> None:
    """List all sprints on board BOARD_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.sprints.list(board_id=board_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def get(
    ctx: typer.Context,
    sprint_id: Annotated[
        int, typer.Argument(metavar="SPRINT_ID", help="Numeric sprint identifier.")
    ],
) -> None:
    """Get one sprint by SPRINT_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.sprints.get(sprint_id=sprint_id), app_ctx.strategy, app_ctx.console
    )
