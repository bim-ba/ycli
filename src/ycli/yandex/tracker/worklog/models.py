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
