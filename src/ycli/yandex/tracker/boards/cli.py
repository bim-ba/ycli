"""`tracker boards` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.cli.typedefs import AllOption, LimitOption  # noqa: TC001
from ycli.yandex.models import Ack
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.boards.models import BoardCreate, BoardUpdate

app = typer.Typer(name="boards", help="Tracker agile boards.", no_args_is_help=True)

BoardIdArg = Annotated[int, typer.Argument(metavar="BOARD_ID", help="Numeric board identifier.")]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    limit: LimitOption = 0,
    all_: AllOption = False,
) -> None:
    """List all agile boards (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = resolve_cap(limit, app_ctx.config.max_items, all_=all_)
    Serializer.serialize(app_ctx.tracker.boards.list(limit=cap), app_ctx.strategy, app_ctx.console)


@app.command()
def get(ctx: typer.Context, board_id: BoardIdArg) -> None:
    """Get one agile board by BOARD_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.boards.get(board_id=board_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help="Name of the new board.")],
    owner: Annotated[str, typer.Option(help="Login or uid of the board owner.")] = "",
    permissions: Annotated[str, typer.Option(help="Access template: 'private' or 'public'.")] = "",
    backlog: Annotated[
        bool | None, typer.Option("--backlog/--no-backlog", help="Enable the board backlog.")
    ] = None,
    sprints: Annotated[
        bool | None, typer.Option("--sprints/--no-sprints", help="Enable board sprints.")
    ] = None,
) -> None:
    """Create an agile board (POST /liveBoards/)."""
    body = BoardCreate(
        name=name,
        owner=owner or None,
        board_permissions_template=permissions or None,
        backlog_available=backlog,
        sprints_available=sprints,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.boards.create(body), app_ctx.strategy, app_ctx.console)


@app.command()
def edit(
    ctx: typer.Context,
    board_id: BoardIdArg,
    name: Annotated[str, typer.Option(help="New board name.")] = "",
    backlog: Annotated[
        bool | None, typer.Option("--backlog/--no-backlog", help="Enable the board backlog.")
    ] = None,
    sprints: Annotated[
        bool | None, typer.Option("--sprints/--no-sprints", help="Enable board sprints.")
    ] = None,
) -> None:
    """Edit an agile board BOARD_ID (PATCH /boards/{board_id}) — only supplied fields are sent."""
    body = BoardUpdate(
        name=name or None,
        backlog_available=backlog,
        sprints_available=sprints,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.boards.edit(board_id, body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def delete(ctx: typer.Context, board_id: BoardIdArg) -> None:
    """Delete an agile board BOARD_ID (DELETE /boards/{board_id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.boards.delete(board_id=board_id)
    Serializer.serialize(Ack.deleted("board", board_id), app_ctx.strategy, app_ctx.console)
