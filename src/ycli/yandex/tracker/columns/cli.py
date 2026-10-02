"""`tracker columns` commands (agile board columns)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.columns.models import Column, ColumnCreate, ColumnList, ColumnUpdate

app = typer.Typer(name="columns", help="Tracker agile board columns.", no_args_is_help=True)

BoardIdArg = Annotated[int, typer.Argument(metavar="BOARD_ID", help="Numeric board identifier.")]
ColumnIdArg = Annotated[int, typer.Argument(metavar="COLUMN_ID", help="Numeric column identifier.")]


@app.command("list")
def list_(board_id: BoardIdArg, *, tracker: TrackerClient) -> ColumnList:
    """List all columns on board BOARD_ID."""
    return tracker.columns.list(board_id=board_id)


@app.command()
def get(board_id: BoardIdArg, column_id: ColumnIdArg, *, tracker: TrackerClient) -> Column:
    """Get one column COLUMN_ID on board BOARD_ID."""
    return tracker.columns.get(board_id=board_id, column_id=column_id)


@app.command()
def create(
    board_id: BoardIdArg,
    name: Annotated[str, typer.Option(help="Name of the new column.")],
    status: Annotated[
        list[str], typer.Option("--status", help="Status key for the column (repeatable).")
    ],
    *,
    tracker: TrackerClient,
) -> Column:
    """Create a column on board BOARD_ID (POST /boards/{board_id}/columns/)."""
    body = ColumnCreate(name=name, statuses=status)
    return tracker.columns.create(board_id, body)


@app.command()
def edit(
    board_id: BoardIdArg,
    column_id: ColumnIdArg,
    name: Annotated[str, typer.Option(help="New column name.")] = "",
    status: Annotated[
        list[str] | None,
        typer.Option("--status", help="Replacement status key (repeatable)."),
    ] = None,
    *,
    tracker: TrackerClient,
) -> Column:
    """Edit column COLUMN_ID on board BOARD_ID (PATCH) — only supplied fields are sent."""
    body = ColumnUpdate(name=name or None, statuses=status or None)
    return tracker.columns.edit(board_id, column_id, body)


@app.command()
def delete(board_id: BoardIdArg, column_id: ColumnIdArg, *, tracker: TrackerClient) -> Ack:
    """Delete column COLUMN_ID on board BOARD_ID (DELETE /boards/{board_id}/columns/{column_id})."""
    tracker.columns.delete(board_id=board_id, column_id=column_id)
    return Ack.deleted("column", column_id, on=f"board {board_id}")
