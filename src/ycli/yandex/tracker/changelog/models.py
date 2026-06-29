"""Pydantic models for Tracker changelog (ChangeField + ChangelogEntry + ChangelogList)."""

from __future__ import annotations

from typing import Any

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
    IdStr,
)


class ChangeField(APIModel):
    """One changed field within a ``ChangelogEntry``.

    ``from``/``to`` are polymorphic (string, object, array, or null depending on the
    field that changed) — typed ``Any`` and passed through verbatim.

    Example:
        >>> ChangeField.model_validate({"field": {"id": "status"}, "to": {"key": "open"}}).field
        'status'
    """

    field: IdStr = None
    from_: Any = Field(default=None, alias="from")
    to: Any = None


class ChangelogEntry(APIModel):
    """A changelog event (``/issues/{key}/changelog`` item).

    Example:
        >>> ChangelogEntry.model_validate(
        ...     {"id": "1", "updatedBy": {"display": "Сава"}, "fields": []}
        ... ).updated_by
        'Сава'
    """

    id: str | None = None
    updated_at: str | None = Field(default=None, alias="updatedAt")
    updated_by: DisplayStr = Field(default=None, alias="updatedBy")
    type: str | None = None
    fields: list[ChangeField] = Field(default_factory=list)


class ChangelogList(RootModel[list[ChangelogEntry]]):
    """A bare JSON array of changelog entries.

    Example:
        >>> ChangelogList.model_validate([{"id": "1"}]).root[0].id
        '1'
    """
