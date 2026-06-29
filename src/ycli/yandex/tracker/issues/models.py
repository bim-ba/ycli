"""Pydantic models for Tracker /issues (Issue + IssueList root model)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
    KeyStr,
)


class Issue(APIModel):
    """A Yandex Tracker issue (``/issues/{key}`` response).

    Example:
        >>> Issue.model_validate({"key": "DE-1", "type": {"key": "task"}}).type
        'task'
    """

    key: str | None = None
    summary: str | None = None
    type: KeyStr = None
    status: KeyStr = None
    priority: KeyStr = None
    epic: KeyStr = None
    parent: KeyStr = None
    queue: KeyStr = None
    assignee: DisplayStr = None
    tags: list[str] = Field(default_factory=list)


class IssueList(RootModel[list[Issue]]):
    """A bare JSON array of issues (``POST /issues/_search`` response).

    Example:
        >>> IssueList.model_validate([{"key": "DE-1"}]).root[0].key
        'DE-1'
    """
