"""Tracker board columns FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.columns.models import Column, ColumnCreate, ColumnUpdate
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    BoardId,
    ColumnId,
    tracker_client,
)

mcp = FastMCP("tracker-columns")


@mcp.tool(name="columns_list", annotations={**RO, "title": "List Tracker board columns"})
def list_(
    board_id: Annotated[
        int, Field(description="Numeric identifier of the board whose columns to list.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Column]:
    """Every column defined on the given agile board.

    Each column carries the issue statuses whose cards land in it. Use this to inspect a board's
    column layout; use ``columns_get`` when you already know a column id, and ``boards_get`` for
    the board itself.
    """
    return client.columns.list(board_id=board_id)


@mcp.tool(name="columns_get", annotations={**RO, "title": "Get Tracker board column"})
def get(
    board_id: Annotated[int, Field(description="Numeric identifier of the board.")],
    column_id: Annotated[int, Field(description="Numeric identifier of the column.")],
    client: TrackerClient = Depends(tracker_client),
) -> Column:
    """Look up a single board column by its numeric id.

    The column includes the issue statuses grouped into it. Use this when you already know the
    board and column ids; use ``columns_list`` to enumerate every column on a board.
    """
    return client.columns.get(board_id=board_id, column_id=column_id)


@mcp.tool(
    name="columns_create",
    annotations={**WRITE, "title": "Create Tracker board column"},
)
def create(
    board_id: BoardId, body: ColumnCreate, client: TrackerClient = Depends(tracker_client)
) -> Column:
    """Add a column to an agile board; returns the new column.

    ``name`` and ``statuses`` (the issue-status keys whose cards land in the column) are
    required; ``limit`` optionally caps the number of issues allowed in the column.
    """
    return client.columns.create(board_id, body)


@mcp.tool(
    name="columns_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker board column"},
)
def update(
    board_id: BoardId,
    column_id: ColumnId,
    body: ColumnUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Column:
    """Edit a board column; only the fields set in ``body`` are changed.

    Get ``column_id`` from ``columns_list``. Returns the updated column.
    """
    return client.columns.update(board_id, column_id, body)


@mcp.tool(
    name="columns_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker board column"},
)
def delete(
    board_id: BoardId, column_id: ColumnId, client: TrackerClient = Depends(tracker_client)
) -> Ack:
    """Permanently remove a column from an agile board (irreversible).

    Returns an acknowledgement on success.
    """
    client.columns.delete(board_id=board_id, column_id=column_id)
    return Ack.deleted("column", column_id, on=f"board {board_id}")
