"""Pydantic models for Tracker sprints (SprintBoardRef + Sprint + SprintList)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class SprintBoardRef(APIModel):
    """The board a sprint belongs to (``board`` object) — id + display name.

    Example:
        >>> SprintBoardRef.model_validate({"id": "3", "display": "My board"}).display
        'My board'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the board.",
    )
    id: str | None = Field(default=None, description="Identifier of the board.")
    display: str | None = Field(default=None, description="Human-readable name of the board.")


class Sprint(APIModel):
    """A sprint (``/boards/{id}/sprints`` item and ``/sprints/{id}``).

    A sprint is a fixed time-box of work on an agile board; ``createdBy`` is flattened
    to its display string, ``board`` is kept as a reference object.

    Example:
        >>> Sprint.model_validate({"id": 4405, "name": "Sprint 1", "status": "in_progress"}).status
        'in_progress'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the sprint.",
    )
    id: int | None = Field(default=None, description="Unique identifier of the sprint.")
    version: int | None = Field(
        default=None,
        description="Sprint version; every change to the sprint increments this number.",
    )
    name: str | None = Field(default=None, description="Name of the sprint.")
    board: SprintBoardRef | None = Field(
        default=None, description="Board whose issues the sprint belongs to."
    )
    status: str | None = Field(
        default=None,
        description="Sprint status: draft (open), in_progress, released (done) or archived.",
    )
    archived: bool | None = Field(
        default=None,
        description="Whether the sprint is archived (true) or still active (false).",
    )
    created_by: DisplayStr = Field(
        default=None,
        alias="createdBy",
        description="Display name of the user who created the sprint.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Sprint creation timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    start_date: str | None = Field(
        default=None,
        alias="startDate",
        description="Planned sprint start date (YYYY-MM-DD).",
    )
    end_date: str | None = Field(
        default=None,
        alias="endDate",
        description="Planned sprint end date (YYYY-MM-DD).",
    )
    start_date_time: str | None = Field(
        default=None,
        alias="startDateTime",
        description="Actual sprint start timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    end_date_time: str | None = Field(
        default=None,
        alias="endDateTime",
        description="Actual sprint end timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )


class SprintList(RootModel[list[Sprint]]):
    """A bare JSON array of sprints — the flat public shape of ``sprints.list()``.

    Example:
        >>> SprintList.model_validate([{"id": 4405, "name": "Sprint 1"}]).root[0].name
        'Sprint 1'
    """


class SprintBoardInput(APIModel):
    """The ``board`` object in a create-sprint body — a board identifier wrapper.

    Example:
        >>> SprintBoardInput(id="1").id
        '1'
    """

    id: str = Field(description="Identifier of the board the sprint belongs to.")


class SprintCreate(APIModel):
    """Typed request body for ``sprints.create`` (``POST /sprints``).

    Example:
        >>> SprintCreate(
        ...     name="New Sprint",
        ...     board=SprintBoardInput(id="1"),
        ...     start_date="2018-10-21",
        ...     end_date="2018-10-24",
        ... ).name
        'New Sprint'
    """

    name: str = Field(description="Name of the new sprint.")
    board: SprintBoardInput = Field(description="Board the sprint belongs to (its id).")
    start_date: str = Field(
        serialization_alias="startDate", description="Planned sprint start date (YYYY-MM-DD)."
    )
    end_date: str = Field(
        serialization_alias="endDate", description="Planned sprint end date (YYYY-MM-DD)."
    )


class SprintUpdate(APIModel):
    """Typed request body for ``sprints.edit`` (``PATCH /sprints/{sprint_id}``).

    Every field is optional; only the fields you set are sent.

    Example:
        >>> SprintUpdate(name="Updated Sprint Name").name
        'Updated Sprint Name'
    """

    name: str | None = Field(default=None, description="New name of the sprint.")
    start_date: str | None = Field(
        default=None,
        serialization_alias="startDate",
        description="New planned start date (YYYY-MM-DD).",
    )
    end_date: str | None = Field(
        default=None,
        serialization_alias="endDate",
        description="New planned end date (YYYY-MM-DD).",
    )
    status: str | None = Field(
        default=None,
        description="New sprint status: draft, in_progress, released or archived.",
    )
