"""Pydantic models for Tracker issue types (IssueType + IssueTypeList)."""

from __future__ import annotations

from pydantic import RootModel

from ycli.models import APIModel


class IssueType(APIModel):
    """An issue type descriptor (``/issuetypes`` item).

    Example:
        >>> IssueType.model_validate({"key": "task", "display": "Task"}).key
        'task'
    """

    key: str | None = None
    display: str | None = None


class IssueTypeList(RootModel[list[IssueType]]):
    """A bare JSON array of issue types.

    Example:
        >>> IssueTypeList.model_validate([{"key": "bug"}]).root[0].key
        'bug'
    """
