"""`tracker projects` commands (legacy Projects API v3; see `tracker entities` for the new one)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import values_option
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.projects.models import Project, ProjectCreate, ProjectStatus, ProjectUpdate
from ycli.yandex.tracker.queues.models import Queue

app = typer.Typer(name="projects", help="Tracker projects (legacy API).", no_args_is_help=True)

ProjectIDArg = Annotated[
    int, typer.Argument(metavar="PROJECT_ID", help="Numeric id of the project.")
]
ExpandOpt = Annotated[str | None, typer.Option(help="Extra blocks to include, e.g. queues.")]
StatusOpt = Annotated[str | None, values_option(ProjectStatus, help="Stage of the project.")]
DescriptionOpt = Annotated[str | None, typer.Option(help="Description of the project.")]
LeadOpt = Annotated[str | None, typer.Option(help="Login or id of the project's lead.")]
StartDateOpt = Annotated[str | None, typer.Option("--start-date", help="Start date (YYYY-MM-DD).")]
EndDateOpt = Annotated[str | None, typer.Option("--end-date", help="End date (YYYY-MM-DD).")]
QueuesOpt = Annotated[str, typer.Option(help="Key of the queue whose issues go into the project.")]


@app.command("list")
def list_(expand: ExpandOpt = None, *, tracker: TrackerClient) -> ItemList[Project]:
    """List the organization's projects (GET /projects)."""
    return tracker.projects.list(expand=expand)


@app.command()
def get(project_id: ProjectIDArg, expand: ExpandOpt = None, *, tracker: TrackerClient) -> Project:
    """Print project PROJECT_ID (GET /projects/{id})."""
    return tracker.projects.get(project_id, expand=expand)


@app.command()
def queues(
    project_id: ProjectIDArg,
    expand: Annotated[
        str | None, typer.Option(help="Extra queue blocks, e.g. all or components,versions.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Queue]:
    """List the queues of project PROJECT_ID (GET /projects/{id}/queues)."""
    return tracker.projects.queues(project_id, expand=expand)


@app.command()
def create(
    name: Annotated[str, typer.Option(help="Name of the project.")],
    queues: QueuesOpt,
    description: DescriptionOpt = None,
    lead: LeadOpt = None,
    status: StatusOpt = None,
    start_date: StartDateOpt = None,
    end_date: EndDateOpt = None,
    *,
    tracker: TrackerClient,
) -> Project:
    """Create a project (POST /projects)."""
    body = ProjectCreate(
        name=name,
        queues=queues,
        description=description,
        lead=lead,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    return tracker.projects.create(body)


@app.command()
def update(
    project_id: ProjectIDArg,
    version: Annotated[int, typer.Option(help="Current version of the project (required).")],
    queues: QueuesOpt,
    name: Annotated[str | None, typer.Option(help="New name of the project.")] = None,
    description: DescriptionOpt = None,
    lead: LeadOpt = None,
    status: StatusOpt = None,
    start_date: StartDateOpt = None,
    end_date: EndDateOpt = None,
    expand: ExpandOpt = None,
    *,
    tracker: TrackerClient,
) -> Project:
    """Edit project PROJECT_ID (PUT /projects/{id}?version=); only the given options change."""
    body = ProjectUpdate(
        queues=queues,
        name=name,
        description=description,
        lead=lead,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    return tracker.projects.update(project_id, body, version=version, expand=expand)


@app.command()
def delete(project_id: ProjectIDArg, *, tracker: TrackerClient) -> Ack:
    """Delete project PROJECT_ID (DELETE /projects/{id})."""
    tracker.projects.delete(project_id)
    return Ack.deleted("project", project_id)
