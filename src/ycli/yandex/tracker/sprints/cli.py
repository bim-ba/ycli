"""`tracker sprints` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.models import Ack
from ycli.yandex.tracker.sprints.models import SprintBoardInput, SprintCreate, SprintUpdate

app = typer.Typer(name="sprints", help="Tracker board sprints.", no_args_is_help=True)

SprintIdArg = Annotated[int, typer.Argument(metavar="SPRINT_ID", help="Numeric sprint identifier.")]
VersionOpt = Annotated[
    int | None, typer.Option(help="Current sprint version for the optimistic lock (?version=).")
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    board_id: Annotated[int, typer.Argument(metavar="BOARD_ID", help="Numeric board identifier.")],
) -> None:
    """List all sprints on board BOARD_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.sprints.list(board_id=board_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def get(ctx: typer.Context, sprint_id: SprintIdArg) -> None:
    """Get one sprint by SPRINT_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.sprints.get(sprint_id=sprint_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def create(
    ctx: typer.Context,
    board_id: Annotated[str, typer.Option(help="Identifier of the board the sprint belongs to.")],
    name: Annotated[str, typer.Option(help="Name of the new sprint.")],
    start_date: Annotated[str, typer.Option(help="Planned start date (YYYY-MM-DD).")],
    end_date: Annotated[str, typer.Option(help="Planned end date (YYYY-MM-DD).")],
) -> None:
    """Create a sprint (POST /sprints)."""
    body = SprintCreate(
        name=name,
        board=SprintBoardInput(id=board_id),
        start_date=start_date,
        end_date=end_date,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.sprints.create(body), app_ctx.strategy, app_ctx.console)


@app.command()
def edit(
    ctx: typer.Context,
    sprint_id: SprintIdArg,
    name: Annotated[str, typer.Option(help="New sprint name.")] = "",
    start_date: Annotated[str, typer.Option(help="New start date (YYYY-MM-DD).")] = "",
    end_date: Annotated[str, typer.Option(help="New end date (YYYY-MM-DD).")] = "",
    status: Annotated[
        str, typer.Option(help="New status: draft/in_progress/released/archived.")
    ] = "",
    version: VersionOpt = None,
) -> None:
    """Edit a sprint SPRINT_ID (PATCH /sprints/{id}?version=) — only supplied fields are sent."""
    body = SprintUpdate(
        name=name or None,
        start_date=start_date or None,
        end_date=end_date or None,
        status=status or None,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.sprints.edit(sprint_id, body, version=version),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(ctx: typer.Context, sprint_id: SprintIdArg) -> None:
    """Delete a sprint SPRINT_ID (DELETE /sprints/{sprint_id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.sprints.delete(sprint_id=sprint_id)
    Serializer.serialize(
        Ack(detail=f"deleted sprint {sprint_id}"), app_ctx.strategy, app_ctx.console
    )


@app.command()
def start(ctx: typer.Context, sprint_id: SprintIdArg, version: VersionOpt = None) -> None:
    """Start a sprint SPRINT_ID (POST /sprints/{id}/_start?version=; status → in_progress)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.sprints.start(sprint_id=sprint_id, version=version),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def archive(ctx: typer.Context, sprint_id: SprintIdArg, version: VersionOpt = None) -> None:
    """Archive a sprint SPRINT_ID (POST /sprints/{id}/_archive?version=; status → archived)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.sprints.archive(sprint_id=sprint_id, version=version),
        app_ctx.strategy,
        app_ctx.console,
    )
