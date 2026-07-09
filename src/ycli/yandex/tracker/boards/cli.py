"""`tracker boards` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="boards", help="Tracker agile boards.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option(help="Max boards (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every board (no cap).")] = False,
) -> None:
    """List all agile boards (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(app_ctx.tracker.boards.list(limit=cap), app_ctx.strategy, app_ctx.console)


@app.command()
def get(
    ctx: typer.Context,
    board_id: Annotated[int, typer.Argument(metavar="BOARD_ID", help="Numeric board identifier.")],
) -> None:
    """Get one agile board by BOARD_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.boards.get(board_id=board_id), app_ctx.strategy, app_ctx.console
    )
