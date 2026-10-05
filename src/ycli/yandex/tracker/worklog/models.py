"""Pydantic models for Tracker worklog (Worklog + ItemList[Worklog])."""

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

    id: int | str | None = Field(default=None, description="Worklog record identifier.")
    created_at: str | None = Field(
        default=None, alias="createdAt", description="When the record was created (ISO 8601)."
    )
    created_by: DisplayStr = Field(
        default=None, alias="createdBy", description="Display name of the record author."
    )
    duration: str | None = Field(
        default=None, description="Time spent as an ISO-8601 duration, e.g. ``PT2H``."
    )
    start: str | None = Field(default=None, description="When the work started (ISO 8601).")
    comment: str | None = Field(default=None, description="Note saved with the record.")


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
    start: str = Field(description="Work start time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
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


class ImportWorklog(RequestBody):
    """Typed body for ``POST /issues/{key}/worklogs/_import`` — import one worklog with history.

    Examples:
        >>> ImportWorklog(
        ...     duration="PT1H",
        ...     created_at="2025-02-18T16:35:41.740+0000",
        ...     created_by="username",
        ...     start="2025-02-18T16:35:41.740+0000",
        ... ).model_dump(exclude_none=True)  # doctest: +NORMALIZE_WHITESPACE
        {'duration': 'PT1H', 'createdAt': '2025-02-18T16:35:41.740+0000',
         'createdBy': 'username', 'start': '2025-02-18T16:35:41.740+0000'}
    """

    duration: str = Field(description="Time spent as an ISO-8601 duration, e.g. ``PT1H``.")
    created_at: str = Field(alias="createdAt", description="Original record creation time.")
    created_by: str = Field(alias="createdBy", description="Login or id of the record author.")
    start: str = Field(description="Work start time (``YYYY-MM-DDThh:mm:ss.sss±hhmm``).")
    comment: str | None = Field(default=None, description="Optional note saved in the time report.")
