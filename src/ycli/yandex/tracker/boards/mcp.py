"""Tracker boards FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.tracker.boards.models import Board, BoardList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, app_config, tracker_client

mcp = FastMCP("tracker-boards")


@mcp.tool(name="boards_list", annotations={**RO, "title": "List Tracker boards"}, tags=TAGS)
def list_(
    limit: Annotated[
        int,
        Field(description="Max boards to return; 0 means the YCLI_MAX_ITEMS cap (default 500)."),
    ] = 0,
    client: TrackerClient = Depends(tracker_client),
    cfg: AppConfig = Depends(app_config),
) -> BoardList:
    """All agile boards in the organisation, auto-paginated via the relative id-cursor and sorted
    by ascending board id. Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given. Use
    ``boards_get`` when you know one board id, and ``sprints_list`` to list a board's sprints.

    >>> boards_list(limit=50)  # doctest: +SKIP
    """
    cap = limit or cfg.max_items
    return client.boards.list(limit=cap)


@mcp.tool(name="boards_get", annotations={**RO, "title": "Get Tracker board"}, tags=TAGS)
def get(
    board_id: Annotated[int, Field(description="Numeric identifier of the agile board.")],
    client: TrackerClient = Depends(tracker_client),
) -> Board:
    """Look up a single agile board by its numeric id, including its columns, estimation field and
    burndown calendar. Use this when you already know the board id; use ``boards_list`` to browse
    every board, and ``sprints_list`` to enumerate the sprints defined on this board.

    >>> boards_get(board_id=1)  # doctest: +SKIP
    """
    return client.boards.get(board_id=board_id)
