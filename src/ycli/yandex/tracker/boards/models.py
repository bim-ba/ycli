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
