"""Pydantic models for Tracker board columns (KeyedReference + Column + ColumnList + inputs)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel
from ycli.yandex.tracker.models import KeyedReference


class Column(APIModel):
    """A board column (``/boards/{id}/columns`` item and ``/boards/{id}/columns/{id}``).

    A column groups issue cards by their status; ``statuses`` lists the issue statuses
    whose cards land in this column.

    Examples:
        >>> Column.model_validate({"id": 1, "name": "Open"}).name
        'Open'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the column.",
    )
    id: int | None = Field(default=None, description="Unique identifier of the column.")
    name: str | None = Field(default=None, description="Name of the column.")
    statuses: list[KeyedReference] = Field(
        default_factory=list,
        description="Issue statuses whose cards are shown in this column.",
    )


class ColumnList(RootModel[list[Column]]):
    """A bare JSON array of columns — the flat public shape of ``columns.list()``.

    Examples:
        >>> ColumnList.model_validate([{"id": 1, "name": "Open"}]).root[0].name
        'Open'
    """


class ColumnCreate(APIModel):
    """Typed request body for ``columns.create`` (``POST /boards/{board_id}/columns/``).

    Examples:
        >>> ColumnCreate(name="Approve", statuses=["needInfo", "adjustment"]).name
        'Approve'
    """

    name: str = Field(description="Name of the new column.")
    statuses: list[str] = Field(
        description="Keys of the issue statuses whose cards appear in the column.",
    )


class ColumnUpdate(APIModel):
    """Typed request body for ``columns.edit`` (``PATCH /boards/{board_id}/columns/{column_id}``).

    Every field is optional; only the fields you set are sent.

    Examples:
        >>> ColumnUpdate(name="Pause").name
        'Pause'
    """

    name: str | None = Field(default=None, description="New name of the column.")
    statuses: list[str] | None = Field(
        default=None,
        description="Replacement keys of the issue statuses whose cards appear in the column.",
    )
