"""Pydantic models for Tracker /issues (Issue + IssueList root model)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.models import APIModel
from ycli.yandex.tracker._models import (  # noqa: TC001  # pydantic resolves field types via get_type_hints() at runtime
    _DisplayRef,
    _KeyRef,
)


class Issue(APIModel):
    """A Yandex Tracker issue (``/issues/{key}`` response).

    Nested ``type``/``status``/``priority``/``epic``/``parent``/``queue`` each expose a
    ``.key`` accessor; ``assignee`` exposes ``.display``.

    Example:
        >>> Issue.model_validate({"key": "DE-1", "type": {"key": "task"}}).type_key
        'task'
    """

    key: str | None = None
    summary: str | None = None
    type: _KeyRef | None = None
    status: _KeyRef | None = None
    priority: _KeyRef | None = None
    epic: _KeyRef | None = None
    parent: _KeyRef | None = None
    queue: _KeyRef | None = None
    assignee: _DisplayRef | None = None
    tags: list[str] = Field(default_factory=list)

    @property
    def type_key(self) -> str | None:
        """``type.key`` or ``None``."""
        return self.type.key if self.type else None

    @property
    def status_key(self) -> str | None:
        """``status.key`` or ``None``."""
        return self.status.key if self.status else None

    @property
    def priority_key(self) -> str | None:
        """``priority.key`` or ``None``."""
        return self.priority.key if self.priority else None

    @property
    def epic_key(self) -> str | None:
        """``epic.key`` or ``None``."""
        return self.epic.key if self.epic else None

    @property
    def parent_key(self) -> str | None:
        """``parent.key`` or ``None``."""
        return self.parent.key if self.parent else None

    @property
    def queue_key(self) -> str | None:
        """``queue.key`` or ``None``."""
        return self.queue.key if self.queue else None

    @property
    def assignee_display(self) -> str | None:
        """``assignee.display`` or ``None``."""
        return self.assignee.display if self.assignee else None


class IssueList(RootModel[list[Issue]]):
    """A bare JSON array of issues (``POST /issues/_search`` response).

    Example:
        >>> IssueList.model_validate([{"key": "DE-1"}]).root[0].key
        'DE-1'
    """
