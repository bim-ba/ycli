"""`tracker columns` commands (agile board columns)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.columns.models import ColumnCreate, ColumnUpdate

app = typer.Typer(name="columns", help="Tracker agile board columns.", no_args_is_help=True)

BoardIdArg = Annotated[int, typer.Argument(metavar="BOARD_ID", help="Numeric board identifier.")]
ColumnIdArg = Annotated[int, typer.Argument(metavar="COLUMN_ID", help="Numeric column identifier.")]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context, board_id: BoardIdArg) -> None:
    """List all columns on board BOARD_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.columns.list(board_id=board_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def get(ctx: typer.Context, board_id: BoardIdArg, column_id: ColumnIdArg) -> None:
    """Get one column COLUMN_ID on board BOARD_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.columns.get(board_id=board_id, column_id=column_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def create(
    ctx: typer.Context,
    board_id: BoardIdArg,
    name: Annotated[str, typer.Option(help="Name of the new column.")],
    status: Annotated[
        list[str], typer.Option("--status", help="Status key for the column (repeatable).")
    ],
) -> None:
    """Create a column on board BOARD_ID (POST /boards/{board_id}/columns/)."""
    body = ColumnCreate(name=name, statuses=status)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.columns.create(board_id, body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def edit(
    ctx: typer.Context,
    board_id: BoardIdArg,
    column_id: ColumnIdArg,
    name: Annotated[str, typer.Option(help="New column name.")] = "",
    status: Annotated[
        list[str] | None,
        typer.Option("--status", help="Replacement status key (repeatable)."),
    ] = None,
) -> None:
    """Edit column COLUMN_ID on board BOARD_ID (PATCH) — only supplied fields are sent."""
    body = ColumnUpdate(name=name or None, statuses=status or None)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.columns.edit(board_id, column_id, body),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(ctx: typer.Context, board_id: BoardIdArg, column_id: ColumnIdArg) -> None:
    """Delete column COLUMN_ID on board BOARD_ID (DELETE /boards/{board_id}/columns/{column_id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.columns.delete(board_id=board_id, column_id=column_id)
    print(f"Deleted column {column_id} on board {board_id}")
