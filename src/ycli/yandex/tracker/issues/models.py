"""Pydantic models for Tracker /issues (Issue + IssueList root model)."""

from __future__ import annotations

from pydantic import ConfigDict, Field, RootModel

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
    description: str | None = None
    created_at: str | None = Field(default=None, alias="createdAt")
    created_by: DisplayStr = Field(default=None, alias="createdBy")


class IssueList(RootModel[list[Issue]]):
    """A bare JSON array of issues (``POST /issues/_search`` response).

    Example:
        >>> IssueList.model_validate([{"key": "DE-1"}]).root[0].key
        'DE-1'
    """


class IssueCreate(APIModel):
    """Typed request body for ``POST /issues/`` (create an issue).

    Covers the common fields; ``extra="allow"`` lets any custom (global or queue-local) field
    key=value pair pass through unvalidated, matching the CLI's ``-F key=value`` escape hatch.
    ``type``/``priority`` accept either a bare key string or a ``{"key": ...}`` object (both are
    valid per the Tracker API); the CLI sends the object form.

    Example:
        >>> IssueCreate(queue="TEST", summary="Do it").model_dump(exclude_none=True)
        {'queue': 'TEST', 'summary': 'Do it'}
    """

    model_config = ConfigDict(extra="allow")

    queue: str = Field(description="Key of the target queue.")
    summary: str = Field(description="Issue title.")
    type: dict[str, str] | str | None = Field(
        default=None, description="Issue type — {'key': ...} object or a bare type key."
    )
    priority: dict[str, str] | str | None = Field(
        default=None, description="Priority — {'key': ...} object or a bare priority key."
    )
    parent: str | None = Field(default=None, description="Parent issue key.")
    description: str | None = Field(default=None, description="Issue description (YFM markdown).")
    tags: list[str] | dict[str, list[str]] | None = Field(
        default=None,
        description="Tags — a replace list, or an {'add'|'set'|'remove': [...]} operator edit.",
    )


class IssueUpdate(APIModel):
    """Typed request body for ``PATCH /issues/{key}`` (update an issue; only sent fields change).

    ``extra="allow"`` lets any custom field key=value pair pass through, matching the CLI's
    ``-F key=value`` escape hatch. Status is NOT changed here — use ``transitions_execute``.

    Example:
        >>> IssueUpdate(summary="New title").model_dump(exclude_none=True)
        {'summary': 'New title'}
    """

    model_config = ConfigDict(extra="allow")

    summary: str | None = Field(default=None, description="New summary (title).")
    type: dict[str, str] | str | None = Field(
        default=None, description="New issue type — {'key': ...} object or a bare type key."
    )
    priority: dict[str, str] | str | None = Field(
        default=None, description="New priority — {'key': ...} object or a bare priority key."
    )
    parent: str | None = Field(default=None, description="New parent issue key.")
    description: str | None = Field(
        default=None, description="New issue description (YFM markdown)."
    )
    tags: list[str] | dict[str, list[str]] | None = Field(
        default=None,
        description="New tags — a replace list, or an {'add'|'set'|'remove': [...]} operator edit.",
    )


class ScrollClear(RootModel[dict[str, str]]):
    """A bare ``{scrollId: scrollToken}`` mapping — body for ``POST …/scroll/_clear``.

    Each entry releases the server resources of one scrolled ``issues.search`` response.

    Example:
        >>> ScrollClear({"3ce1-...": "eyJvZmZzZXQi..."}).model_dump()
        {'3ce1-...': 'eyJvZmZzZXQi...'}
    """
