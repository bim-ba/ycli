"""`tracker boards` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.boards.models import Board, BoardCreate, BoardUpdate
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.typedefs import BoardIDArg

app = typer.Typer(name="boards", help="Tracker agile boards.", no_args_is_help=True)


@app.command("list")
def list_(
    limit: LimitOption = None, all_: AllOption = False, *, config: AppConfig, tracker: TrackerClient
) -> ItemList[Board]:
    """List all agile boards (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.boards.list(limit=cap)


@app.command()
def get(board_id: BoardIDArg, *, tracker: TrackerClient) -> Board:
    """Get one agile board by BOARD_ID."""
    return tracker.boards.get(board_id=board_id)


@app.command()
def create(
    name: Annotated[str, typer.Option(help="Name of the new board.")],
    owner: Annotated[str | None, typer.Option(help="Login or uid of the board owner.")] = None,
    permissions: Annotated[
        str | None, typer.Option(help="Access template: 'private' or 'public'.")
    ] = None,
    backlog: Annotated[
        bool | None, typer.Option("--backlog/--no-backlog", help="Enable the board backlog.")
    ] = None,
    sprints: Annotated[
        bool | None, typer.Option("--sprints/--no-sprints", help="Enable board sprints.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Board:
    """Create an agile board (POST /liveBoards/)."""
    body = BoardCreate(
        name=name,
        owner=owner,
        board_permissions_template=permissions,
        backlog_available=backlog,
        sprints_available=sprints,
    )
    return tracker.boards.create(body)


@app.command()
def update(
    board_id: BoardIDArg,
    name: Annotated[str | None, typer.Option(help="New board name.")] = None,
    backlog: Annotated[
        bool | None, typer.Option("--backlog/--no-backlog", help="Enable the board backlog.")
    ] = None,
    sprints: Annotated[
        bool | None, typer.Option("--sprints/--no-sprints", help="Enable board sprints.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Board:
    """Edit an agile board BOARD_ID (PATCH /boards/{board_id}) — only supplied fields are sent."""
    body = BoardUpdate(
        name=name,
        backlog_available=backlog,
        sprints_available=sprints,
    )
    return tracker.boards.update(board_id, body)


@app.command()
def delete(board_id: BoardIDArg, *, tracker: TrackerClient) -> Ack:
    """Delete an agile board BOARD_ID (DELETE /boards/{board_id})."""
    tracker.boards.delete(board_id=board_id)
    return Ack.deleted("board", board_id)
