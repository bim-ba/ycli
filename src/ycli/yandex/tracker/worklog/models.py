"""Pydantic models for Tracker worklog (Worklog + WorklogList)."""
from __future__ import annotations

from pydantic import Field, RootModel

from ycli.models import APIModel
from ycli.yandex.tracker._models import _DisplayRef


class Worklog(APIModel):
    """A worklog entry (``/issues/{key}/worklog`` item).

    Example:
        >>> Worklog.model_validate({"id": 5, "createdBy": {"display": "X"}, "duration": "PT2H"}).author_display
        'X'
    """

    id: int | str | None = None
    created_at: str | None = Field(default=None, alias="createdAt")
    created_by: _DisplayRef | None = Field(default=None, alias="createdBy")
    duration: str | None = None
    start: str | None = None
    comment: str | None = None

    @property
    def author_display(self) -> str | None:
        """``createdBy.display`` or ``None``."""
        return self.created_by.display if self.created_by else None


class WorklogList(RootModel[list[Worklog]]):
    """A bare JSON array of worklog entries.

    Example:
        >>> WorklogList.model_validate([{"duration": "PT1H"}]).root[0].duration
        'PT1H'
    """
