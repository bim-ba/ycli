"""Tracker board columns FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.columns.models import Column, ColumnCreate, ColumnList, ColumnUpdate
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)

mcp = FastMCP("tracker-columns")


@mcp.tool(name="columns_list", annotations={**RO, "title": "List Tracker board columns"}, tags=TAGS)
def list_(
    board_id: Annotated[
        int, Field(description="Numeric identifier of the board whose columns to list.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> ColumnList:
    """Every column defined on the given agile board, each with the issue statuses whose cards land
    in it. Use this to inspect a board's column layout; use ``columns_get`` when you already know a
    column id, and ``boards_get`` for the board itself.

    >>> columns_list(board_id=73)  # doctest: +SKIP
    """
    return client.columns.list(board_id=board_id)


@mcp.tool(name="columns_get", annotations={**RO, "title": "Get Tracker board column"}, tags=TAGS)
def get(
    board_id: Annotated[int, Field(description="Numeric identifier of the board.")],
    column_id: Annotated[int, Field(description="Numeric identifier of the column.")],
    client: TrackerClient = Depends(tracker_client),
) -> Column:
    """Look up a single board column by its numeric id, including the issue statuses grouped into
    it. Use this when you already know the board and column ids; use ``columns_list`` to enumerate
    every column on a board.

    >>> columns_get(board_id=73, column_id=1)  # doctest: +SKIP
    """
    return client.columns.get(board_id=board_id, column_id=column_id)


@mcp.tool(
    name="columns_create",
    annotations={**WRITE, "title": "Create Tracker board column"},
    tags=WRITE_TAGS,
)
def create(
    board_id: int, body: ColumnCreate, client: TrackerClient = Depends(tracker_client)
) -> Column:
    """Add a column to an agile board; returns the new column.

    ``name`` and ``statuses`` (the issue-status keys whose cards land in the column) are
    required; ``limit`` optionally caps the number of issues allowed in the column.
    """
    return client.columns.create(board_id, body)


@mcp.tool(
    name="columns_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker board column"},
    tags=WRITE_TAGS,
)
def edit(
    board_id: int,
    column_id: int,
    body: ColumnUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Column:
    """Edit a board column; only the fields set in ``body`` are changed.

    Get ``column_id`` from ``columns_list``. Returns the updated column.
    """
    return client.columns.edit(board_id, column_id, body)


@mcp.tool(
    name="columns_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker board column"},
    tags=WRITE_TAGS,
)
def delete(board_id: int, column_id: int, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently remove a column from an agile board (irreversible).

    Returns an acknowledgement on success.
    """
    client.columns.delete(board_id=board_id, column_id=column_id)
    return Ack.deleted("column", column_id, on=f"board {board_id}")
