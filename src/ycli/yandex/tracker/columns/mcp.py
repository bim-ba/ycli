"""Tracker board columns FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.columns.models import Column, ColumnList
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client

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
    column id, and ``boards_get`` for the board itself. Columns are created/edited via the CLI/SDK.

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
