"""Tracker boards FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.boards.models import Board, BoardCreate, BoardUpdate
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    BoardId,
    app_config,
    tracker_client,
)

mcp = FastMCP("tracker-boards")


@mcp.tool(name="boards_list", annotations={**RO, "title": "List Tracker boards"}, tags=TAGS)
def list_(
    limit: Annotated[
        int | None,
        Field(ge=1, description=f"Max boards to return; {LIMIT_CAP}"),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Board]:
    """All agile boards in the organisation, sorted by ascending board id.

    Auto-paginated via the relative id-cursor. Capped at the configured item cap unless ``limit``
    is given. Use ``boards_get`` when you know one board id, and ``sprints_list`` to list a
    board's sprints.
    """
    cap = config.http.cap(limit)
    return client.boards.list(limit=cap)


@mcp.tool(name="boards_get", annotations={**RO, "title": "Get Tracker board"}, tags=TAGS)
def get(
    board_id: Annotated[int, Field(description="Numeric identifier of the agile board.")],
    client: TrackerClient = Depends(tracker_client),
) -> Board:
    """Look up a single agile board by its numeric id.

    The board includes its columns, estimation field and burndown calendar. Use this when you
    already know the board id; use ``boards_list`` to browse every board, and ``sprints_list`` to
    enumerate the sprints defined on this board.
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
    name="boards_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker board"},
    tags=WRITE_TAGS,
)
def update(
    board_id: BoardId, body: BoardUpdate, client: TrackerClient = Depends(tracker_client)
) -> Board:
    """Edit an agile board; only the fields set in ``body`` are changed.

    Supports renaming, toggling ``backlog_available``/``sprints_available`` and replacing the
    ``columns`` layout. Returns the updated board.
    """
    return client.boards.update(board_id, body)


@mcp.tool(
    name="boards_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker board"},
    tags=WRITE_TAGS,
)
def delete(board_id: BoardId, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete an agile board (irreversible; its issues are not affected).

    Returns an acknowledgement on success.
    """
    client.boards.delete(board_id=board_id)
    return Ack.deleted("board", board_id)
