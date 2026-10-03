"""Pydantic models for Tracker worklog (Worklog + ItemList[Worklog])."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from ycli.yandex.models import (
    APIModel,
    DisplayStr,
    RequestBody,  # pydantic resolves field types via get_type_hints() at runtime
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


class WorklogCreate(RequestBody):
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


class WorklogUpdate(RequestBody):
    """Typed request body for ``PATCH /issues/{key}/worklog/{record_id}`` (edit an entry).

    Examples:
        >>> WorklogUpdate(duration="PT30M").model_dump(exclude_none=True)
        {'duration': 'PT30M'}
    """

    duration: str | None = Field(
        default=None, description="New time spent as an ISO-8601 duration, e.g. PT30M."
    )
    comment: str | None = Field(default=None, description="New note for the time-tracking report.")


class WorklogPeriod(RequestBody):
    """A range of creation times (``createdAt`` of a worklog search).

    Examples:
        >>> period = WorklogPeriod.model_validate({"from": "2026-01-01T00:00:00"})
        >>> period.model_dump(exclude_none=True)
        {'from': '2026-01-01T00:00:00'}
    """

    start: str | None = Field(
        default=None,
        alias="from",
        description="Start of the range, ``YYYY-MM-DDThh:mm:ss``.",
    )
    end: str | None = Field(
        default=None,
        alias="to",
        description="End of the range, ``YYYY-MM-DDThh:mm:ss``.",
    )


class WorklogSearch(RequestBody):
    """Typed request body for ``POST /worklog/_search``: by author, by creation time, or both.

    Examples:
        >>> WorklogSearch.model_validate({"createdBy": "ann"}).model_dump(exclude_none=True)
        {'createdBy': 'ann'}
    """

    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="Login or id of the author of the records.",
    )
    created_at: WorklogPeriod | None = Field(
        default=None, alias="createdAt", description="When the records were created."
    )
