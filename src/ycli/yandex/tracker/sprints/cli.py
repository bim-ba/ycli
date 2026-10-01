"""`tracker sprints` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.sprints.models import (
    Sprint,
    SprintBoardInput,
    SprintCreate,
    SprintList,
    SprintUpdate,
)

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
    board_id: Annotated[int, typer.Argument(metavar="BOARD_ID", help="Numeric board identifier.")],
    *,
    tracker: TrackerClient,
) -> SprintList:
    """List all sprints on board BOARD_ID."""
    return tracker.sprints.list(board_id=board_id)


@app.command()
def get(sprint_id: SprintIdArg, *, tracker: TrackerClient) -> Sprint:
    """Get one sprint by SPRINT_ID."""
    return tracker.sprints.get(sprint_id=sprint_id)


@app.command()
def create(
    board_id: Annotated[str, typer.Option(help="Identifier of the board the sprint belongs to.")],
    name: Annotated[str, typer.Option(help="Name of the new sprint.")],
    start_date: Annotated[str, typer.Option(help="Planned start date (YYYY-MM-DD).")],
    end_date: Annotated[str, typer.Option(help="Planned end date (YYYY-MM-DD).")],
    *,
    tracker: TrackerClient,
) -> Sprint:
    """Create a sprint (POST /sprints)."""
    body = SprintCreate(
        name=name,
        board=SprintBoardInput(id=board_id),
        start_date=start_date,
        end_date=end_date,
    )
    return tracker.sprints.create(body)


@app.command()
def edit(
    sprint_id: SprintIdArg,
    name: Annotated[str, typer.Option(help="New sprint name.")] = "",
    start_date: Annotated[str, typer.Option(help="New start date (YYYY-MM-DD).")] = "",
    end_date: Annotated[str, typer.Option(help="New end date (YYYY-MM-DD).")] = "",
    status: Annotated[
        str, typer.Option(help="New status: draft/in_progress/released/archived.")
    ] = "",
    version: VersionOpt = None,
    *,
    tracker: TrackerClient,
) -> Sprint:
    """Edit a sprint SPRINT_ID (PATCH /sprints/{id}?version=) — only supplied fields are sent."""
    body = SprintUpdate(
        name=name or None,
        start_date=start_date or None,
        end_date=end_date or None,
        status=status or None,
    )
    return tracker.sprints.edit(sprint_id, body, version=version)


@app.command()
def delete(sprint_id: SprintIdArg, *, tracker: TrackerClient) -> Ack:
    """Delete a sprint SPRINT_ID (DELETE /sprints/{sprint_id})."""
    tracker.sprints.delete(sprint_id=sprint_id)
    return Ack.deleted("sprint", sprint_id)


@app.command()
def start(sprint_id: SprintIdArg, version: VersionOpt = None, *, tracker: TrackerClient) -> Sprint:
    """Start a sprint SPRINT_ID (POST /sprints/{id}/_start?version=; status → in_progress)."""
    return tracker.sprints.start(sprint_id=sprint_id, version=version)


@app.command()
def archive(
    sprint_id: SprintIdArg, version: VersionOpt = None, *, tracker: TrackerClient
) -> Sprint:
    """Archive a sprint SPRINT_ID (POST /sprints/{id}/_archive?version=; status → archived)."""
    return tracker.sprints.archive(sprint_id=sprint_id, version=version)
