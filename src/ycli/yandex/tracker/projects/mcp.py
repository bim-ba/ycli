"""Tracker ``/projects`` FastMCP tools (legacy Projects API v3; honest ARCH-3 annotations)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    new_server,
    tracker_client,
)
from ycli.yandex.tracker.projects.models import Project, ProjectCreate, ProjectUpdate
from ycli.yandex.tracker.queues.models import Queue

mcp = new_server("tracker-projects")

ProjectID = Annotated[int, Field(description="Numeric id of the project, from ``projects_list``.")]
ProjectExpand = Annotated[
    str | None, Field(description="Extra blocks to include, e.g. ``queues``.")
]


@mcp.tool(name="projects_list", annotations={**RO, "title": "List Tracker projects"})
def list_(
    expand: ProjectExpand = None, client: TrackerClient = Depends(tracker_client)
) -> ItemList[Project]:
    """Every project of the organization (the legacy Projects API).

    ``entities_search`` is the newer way to find projects and portfolios.
    """
    return client.projects.list(expand=expand)


@mcp.tool(name="projects_get", annotations={**RO, "title": "Get Tracker project"})
def get(
    project_id: ProjectID,
    expand: ProjectExpand = None,
    client: TrackerClient = Depends(tracker_client),
) -> Project:
    """One project: name, lead, stage, dates and ``version`` (needed to edit it)."""
    return client.projects.get(project_id, expand=expand)


@mcp.tool(
    name="projects_queues_list",
    annotations={**RO, "title": "List queues of a Tracker project"},
)
def queues_list(
    project_id: ProjectID,
    expand: Annotated[
        str | None,
        Field(description="Extra queue blocks, e.g. ``all`` or ``components,versions``."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Queue]:
    """The queues whose issues belong to a project."""
    return client.projects.queues_list(project_id, expand=expand)


@mcp.tool(
    name="projects_create",
    annotations={**WRITE, "title": "Create Tracker project"},
)
def create(body: ProjectCreate, client: TrackerClient = Depends(tracker_client)) -> Project:
    """Create a project (legacy Projects API).

    ``name`` and ``queues`` (a queue key) are required, ``status`` is DRAFT, IN_PROGRESS,
    LAUNCHED or POSTPONED. Returns the project.
    """
    return client.projects.create(body)


@mcp.tool(
    name="projects_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker project"},
)
def update(
    project_id: ProjectID,
    body: ProjectUpdate,
    version: Annotated[
        int, Field(description="Current version of the project, from ``projects_get``.")
    ],
    expand: ProjectExpand = None,
    client: TrackerClient = Depends(tracker_client),
) -> Project:
    """Edit a project; ``queues`` is required on every edit, other fields change when set.

    Returns the project with its incremented version.
    """
    return client.projects.update(project_id, body, version=version, expand=expand)


@mcp.tool(
    name="projects_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker project"},
)
def delete(project_id: ProjectID, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Delete a project (irreversible). Returns an acknowledgement."""
    client.projects.delete(project_id)
    return Ack.deleted("project", project_id)
