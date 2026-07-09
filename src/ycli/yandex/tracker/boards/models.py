"""Pydantic models for Tracker agile boards (BoardColumn + Calendar + Board + BoardList)."""

from __future__ import annotations

from typing import Any

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class BoardColumn(APIModel):
    """One column of an agile board (``columns[]`` item) — a status bucket for cards.

    Example:
        >>> BoardColumn.model_validate({"id": "1", "display": "Open"}).display
        'Open'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns information about the column's task field.",
    )
    id: str | None = Field(default=None, description="Identifier of the column's task field.")
    display: str | None = Field(default=None, description="Human-readable name of the column.")


class Calendar(APIModel):
    """The board's calendar reference — its working-days data feeds the burndown chart.

    Example:
        >>> Calendar.model_validate({"id": 6}).id
        6
    """

    id: int | None = Field(
        default=None, description="Identifier of the calendar used by the board."
    )


class Board(APIModel):
    """An agile board (``/boards/{id}`` and ``/boards/_paginate`` item).

    A board visualises issues as cards grouped into columns by status. Reference objects
    (``createdBy``/``estimateBy``/``country``) are flattened to their display string.

    Example:
        >>> Board.model_validate(
        ...     {"id": 1, "name": "My board", "estimateBy": {"display": "Story Points"}}
        ... ).estimate_by
        'Story Points'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the board.",
    )
    id: int | None = Field(default=None, description="Unique identifier of the board.")
    version: int | None = Field(
        default=None,
        description="Board version; every change to the board increments this number.",
    )
    name: str | None = Field(default=None, description="Name of the board.")
    columns: list[BoardColumn] = Field(
        default_factory=list, description="Columns of the board, one status bucket per column."
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Board creation timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp of the board's most recent update (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    created_by: DisplayStr = Field(
        default=None,
        alias="createdBy",
        description="Display name of the user who created the board.",
    )
    use_ranking: bool | None = Field(
        default=None,
        alias="useRanking",
        description="Deprecated flag: whether reordering cards on the board is allowed.",
    )
    estimate_by: DisplayStr = Field(
        default=None,
        alias="estimateBy",
        description="Deprecated: display name of the issue field used to estimate effort.",
    )
    country: DisplayStr = Field(
        default=None, description="Deprecated: display name of the board's country."
    )
    calendar: Calendar | None = Field(
        default=None, description="Calendar whose working-days data feeds the burndown chart."
    )
    auto_filter_settings: Any = Field(
        default=None,
        alias="autoFilterSettings",
        description="Filter settings that auto-add issues to and remove them from the board.",
    )


class BoardList(RootModel[list[Board]]):
    """A bare JSON array of boards — the flat public shape of ``boards.list()``.

    Example:
        >>> BoardList.model_validate([{"id": 1, "name": "My board"}]).root[0].name
        'My board'
    """


class BoardColumnInput(APIModel):
    """One column in a create/edit board request body (``columns[]`` item).

    Example:
        >>> BoardColumnInput(name="To Do", statuses=["new", "open"]).name
        'To Do'
    """

    name: str = Field(description="Name of the column.")
    statuses: list[str] | None = Field(
        default=None,
        description="Status keys whose issues are shown in this column (names/keys from settings).",
    )
    limit: int | None = Field(
        default=None, description="Maximum number of issues allowed in the column."
    )


class BoardCreate(APIModel):
    """Typed request body for ``boards.create`` (``POST /liveBoards/``).

    ``name`` is the only required field; every other field is omitted from the JSON
    body when left as ``None`` (see ``model_dump(by_alias=True, exclude_none=True)``).

    Example:
        >>> BoardCreate(name="Testing", owner="username").name
        'Testing'
    """

    name: str = Field(description="Name of the new board (required).")
    owner: str | None = Field(
        default=None, description="Login or uid of the board owner (defaults to the caller)."
    )
    board_permissions_template: str | None = Field(
        default=None,
        serialization_alias="boardPermissionsTemplate",
        description="Access template: 'private' (owner only) or 'public' (all staff, the default).",
    )
    backlog_available: bool | None = Field(
        default=None,
        serialization_alias="backlogAvailable",
        description="Whether the board has a backlog enabled (pair with sprintsAvailable).",
    )
    sprints_available: bool | None = Field(
        default=None,
        serialization_alias="sprintsAvailable",
        description="Whether the board has sprints enabled (pair with backlogAvailable).",
    )
    columns: list[BoardColumnInput] | None = Field(
        default=None, description="Status-backed columns of the board, one bucket per column."
    )


class BoardUpdate(APIModel):
    """Typed request body for ``boards.edit`` (``PATCH /boards/{board_id}``).

    Every field is optional; only the fields you set are sent, so an omitted field
    is left unchanged on the board.

    Example:
        >>> BoardUpdate(name="New name").name
        'New name'
    """

    name: str | None = Field(default=None, description="New name of the board.")
    backlog_available: bool | None = Field(
        default=None,
        serialization_alias="backlogAvailable",
        description="Whether the board has a backlog enabled (pair with sprintsAvailable).",
    )
    sprints_available: bool | None = Field(
        default=None,
        serialization_alias="sprintsAvailable",
        description="Whether the board has sprints enabled (pair with backlogAvailable).",
    )
    columns: list[BoardColumnInput] | None = Field(
        default=None, description="Replacement status-backed columns of the board."
    )
