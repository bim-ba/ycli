"""Pydantic models for Tracker worklog (Worklog + WorklogList)."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class Worklog(APIModel):
    """A worklog entry (``/issues/{key}/worklog`` item).

    Examples:
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

    Examples:
        >>> WorklogList.model_validate([{"duration": "PT1H"}]).root[0].duration
        'PT1H'
    """


def _now() -> str:
    """The current local time in Tracker's format.

    Returns:
        The timestamp.

    Examples:
        >>> len(_now()) == len("2026-10-02T10:00:00.000+0700")
        True
    """
    moment = datetime.now().astimezone()
    return f"{moment:%Y-%m-%dT%H:%M:%S}.{moment.microsecond // 1000:03d}{moment:%z}"


class WorklogCreate(APIModel):
    """Typed request body for ``POST /issues/{key}/worklog`` (log time spent).

    Examples:
        >>> WorklogCreate(duration="PT2H", start="2026-10-02T10:00:00.000+0700").model_dump(
        ...     exclude_none=True
        ... )
        {'duration': 'PT2H', 'start': '2026-10-02T10:00:00.000+0700'}
    """

    duration: str = Field(
        description="Time spent as an ISO-8601 duration, e.g. PT2H, PT300M, P1DT3H."
    )
    # Tracker refuses a time report without a start (422 "start: required").
    start: str = Field(
        default_factory=_now,
        description="Work start time, YYYY-MM-DDThh:mm:ss.sss±hhmm; now when omitted.",
    )
    comment: str | None = Field(
        default=None, description="Optional note saved in the time-tracking report."
    )


class WorklogUpdate(APIModel):
    """Typed request body for ``PATCH /issues/{key}/worklog/{record_id}`` (edit an entry).

    Examples:
        >>> WorklogUpdate(duration="PT30M").model_dump(exclude_none=True)
        {'duration': 'PT30M'}
    """

    duration: str | None = Field(
        default=None, description="New time spent as an ISO-8601 duration, e.g. PT30M."
    )
    comment: str | None = Field(default=None, description="New note for the time-tracking report.")
