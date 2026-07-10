"""`wiki operations` commands — read the status of an async page/grid clone."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(
    name="operations", help="Wiki async operation status (clone polling).", no_args_is_help=True
)

TaskIdArg = Annotated[
    str, typer.Argument(metavar="TASK_ID", help="Operation task id (from a clone trigger).")
]


@app.command()
def clone(ctx: typer.Context, task_id: TaskIdArg) -> None:
    """Print a page-clone operation's status (GET /operations/clone/{task_id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.operations.clone_get(task_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def gridclone(ctx: typer.Context, task_id: TaskIdArg) -> None:
    """Print a grid-clone operation's status (GET /operations/clone_inline_grid/{task_id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.operations.gridclone_get(task_id), app_ctx.strategy, app_ctx.console
    )
