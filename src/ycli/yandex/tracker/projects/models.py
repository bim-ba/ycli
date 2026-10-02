"""Pydantic models for Tracker ``/projects`` (Projects API v3).

The docs call this API legacy and point to the unified entities API for projects and
portfolios (``ycli tracker entities``); these models serve the older endpoints.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel
from ycli.yandex.tracker.queues.models import (
    QueueUser,  # pydantic resolves field types at runtime
)


class ProjectStatus(enum.StrEnum):
    """Stage of a project, as a request spells it (replies print it in lower case)."""

    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    LAUNCHED = "LAUNCHED"
    POSTPONED = "POSTPONED"


class Project(APIModel):
    """A Tracker project (``GET /projects/{id}``).

    Examples:
        >>> Project.model_validate({"id": "1", "name": "Launch", "status": "draft"}).status
        'draft'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource URL of the project."
    )
    id: int | str | None = Field(default=None, description="Identifier of the project.")
    version: int | None = Field(
        default=None, description="Version of the project; each change increments it."
    )
    key: str | None = Field(default=None, description="Key of the project; equals its name.")
    name: str | None = Field(default=None, description="Name of the project.")
    description: str | None = Field(
        default=None, description="Description (not shown in the Tracker interface)."
    )
    lead: QueueUser | None = Field(default=None, description="The project's lead.")
    status: str | None = Field(
        default=None, description="Stage: draft, in_progress, launched or postponed."
    )
    start_date: str | None = Field(
        default=None, alias="startDate", description="Start date (YYYY-MM-DD)."
    )
    end_date: str | None = Field(
        default=None, alias="endDate", description="End date (YYYY-MM-DD)."
    )
    queues: list[Any] | None = Field(
        default=None, description="Queues of the project; present with ``expand=queues``."
    )


class ProjectList(RootModel[list[Project]]):
    """A bare JSON array of the organization's projects.

    Examples:
        >>> ProjectList.model_validate([{"id": "1"}]).root[0].id
        '1'
    """


class ProjectCreate(APIModel):
    """Typed request body for ``projects.create`` (``POST /projects``).

    Examples:
        >>> ProjectCreate(name="Launch", queues="TEST").model_dump(by_alias=True, exclude_none=True)
        {'name': 'Launch', 'queues': 'TEST'}
    """

    name: str = Field(description="Name of the project.")
    queues: str = Field(description="Key of the queue whose issues go into the project.")
    description: str | None = Field(default=None, description="Description of the project.")
    lead: str | int | None = Field(default=None, description="Login or id of the project's lead.")
    status: ProjectStatus | None = Field(default=None, description="Stage of the project.")
    start_date: str | None = Field(
        default=None, serialization_alias="startDate", description="Start date (YYYY-MM-DD)."
    )
    end_date: str | None = Field(
        default=None, serialization_alias="endDate", description="End date (YYYY-MM-DD)."
    )


class ProjectUpdate(APIModel):
    """Typed request body for ``projects.edit`` (``PUT /projects/{id}?version=``).

    ``queues`` is required by the API on every edit; the rest change when set.

    Examples:
        >>> ProjectUpdate(queues="TEST", name="Renamed").model_dump(exclude_none=True)
        {'queues': 'TEST', 'name': 'Renamed'}
    """

    queues: str = Field(description="Key of the queue whose issues go into the project.")
    name: str | None = Field(default=None, description="New name of the project.")
    description: str | None = Field(default=None, description="New description of the project.")
    lead: str | int | None = Field(default=None, description="Login or id of the new lead.")
    status: ProjectStatus | None = Field(default=None, description="New stage of the project.")
    start_date: str | None = Field(
        default=None, serialization_alias="startDate", description="New start date (YYYY-MM-DD)."
    )
    end_date: str | None = Field(
        default=None, serialization_alias="endDate", description="New end date (YYYY-MM-DD)."
    )
