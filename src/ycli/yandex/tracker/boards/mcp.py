"""Tracker boards FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.boards.models import Board, BoardCreate, BoardList, BoardUpdate
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    app_config,
    tracker_client,
)

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
    cap = resolve_cap(limit, cfg.max_items)
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


@mcp.tool(
    name="boards_create", annotations={**WRITE, "title": "Create Tracker board"}, tags=WRITE_TAGS
)
def create(body: BoardCreate, client: TrackerClient = Depends(tracker_client)) -> Board:
    """Create an agile board; returns the new board with its id.

    ``name`` is required; optional fields include ``owner``, the ``private``/``public``
    permissions template, the ``backlog_available``/``sprints_available`` flags and status-backed
    ``columns``.
    """
    return client.boards.create(body)


@mcp.tool(
    name="boards_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker board"},
    tags=WRITE_TAGS,
)
def edit(
    board_id: int, body: BoardUpdate, client: TrackerClient = Depends(tracker_client)
) -> Board:
    """Edit an agile board; only the fields set in ``body`` are changed.

    Supports renaming, toggling ``backlog_available``/``sprints_available`` and replacing the
    ``columns`` layout. Returns the updated board.
    """
    return client.boards.edit(board_id, body)


@mcp.tool(
    name="boards_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker board"},
    tags=WRITE_TAGS,
)
def delete(board_id: int, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete an agile board (irreversible; its issues are not affected).

    Returns an acknowledgement on success.
    """
    client.boards.delete(board_id=board_id)
    return Ack(detail=f"deleted board {board_id}")
