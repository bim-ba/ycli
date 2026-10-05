"""Pydantic models for Tracker board columns (Column and its write bodies)."""

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
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


class ColumnCreate(RequestBody):
    """Typed request body for ``columns.create`` (``POST /boards/{board_id}/columns/``).

    Examples:
        >>> ColumnCreate(name="Approve", statuses=["needInfo", "adjustment"]).name
        'Approve'
    """

    name: str = Field(description="Name of the new column.")
    statuses: list[str] = Field(
        description="Keys of the issue statuses whose cards appear in the column.",
    )


class ColumnUpdate(RequestBody):
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
