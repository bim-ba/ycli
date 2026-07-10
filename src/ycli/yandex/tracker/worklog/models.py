"""Pydantic models for Tracker worklog (Worklog + WorklogList)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class Worklog(APIModel):
    """A worklog entry (``/issues/{key}/worklog`` item).

    Example:
        >>> Worklog.model_validate(
        ...     {"id": 5, "createdBy": {"display": "X"}, "duration": "PT2H"}
        ... ).created_by
        'X'
    """

    id: int | str | None = None
    created_at: str | None = Field(default=None, alias="createdAt")
    created_by: DisplayStr = Field(default=None, alias="createdBy")
    duration: str | None = None
    start: str | None = None
    comment: str | None = None


class WorklogList(RootModel[list[Worklog]]):
    """A bare JSON array of worklog entries.

    Example:
        >>> WorklogList.model_validate([{"duration": "PT1H"}]).root[0].duration
        'PT1H'
    """


class WorklogCreate(APIModel):
    """Typed request body for ``POST /issues/{key}/worklog`` (log time spent).

    Example:
        >>> WorklogCreate(duration="PT2H").model_dump(exclude_none=True)
        {'duration': 'PT2H'}
    """

    duration: str = Field(
        description="Time spent as an ISO-8601 duration, e.g. PT2H, PT300M, P1DT3H."
    )
    start: str | None = Field(
        default=None, description="Work start time, YYYY-MM-DDThh:mm:ss.sss±hhmm."
    )
    comment: str | None = Field(
        default=None, description="Optional note saved in the time-tracking report."
    )


class WorklogUpdate(APIModel):
    """Typed request body for ``PATCH /issues/{key}/worklog/{record_id}`` (edit an entry).

    Example:
        >>> WorklogUpdate(duration="PT30M").model_dump(exclude_none=True)
        {'duration': 'PT30M'}
    """

    duration: str | None = Field(
        default=None, description="New time spent as an ISO-8601 duration, e.g. PT30M."
    )
    comment: str | None = Field(default=None, description="New note for the time-tracking report.")
