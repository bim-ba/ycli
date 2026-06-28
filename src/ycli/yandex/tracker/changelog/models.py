"""Pydantic models for Tracker changelog (ChangeField + ChangelogEntry + ChangelogList)."""

from __future__ import annotations

from typing import Any

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel
from ycli.yandex.tracker._models import (  # noqa: TC001  # pydantic resolves field types via get_type_hints() at runtime
    _DisplayRef,
    _IdRef,
)


class ChangeField(APIModel):
    """One changed field within a ``ChangelogEntry``.

    ``from``/``to`` are polymorphic (string, object, array, or null depending on the
    field that changed) — typed ``Any`` and passed through verbatim.

    Example:
        >>> ChangeField.model_validate({"field": {"id": "status"}, "to": {"key": "open"}}).field_id
        'status'
    """

    field: _IdRef | None = None
    from_: Any = Field(default=None, alias="from")
    to: Any = None

    @property
    def field_id(self) -> str | None:
        """``field.id`` or ``None``."""
        return self.field.id if self.field else None


class ChangelogEntry(APIModel):
    """A changelog event (``/issues/{key}/changelog`` item).

    Example:
        >>> ChangelogEntry.model_validate(
        ...     {"id": "1", "updatedBy": {"display": "Сава"}, "fields": []}
        ... ).author_display
        'Сава'
    """

    id: str | None = None
    updated_at: str | None = Field(default=None, alias="updatedAt")
    updated_by: _DisplayRef | None = Field(default=None, alias="updatedBy")
    type: str | None = None
    fields: list[ChangeField] = Field(default_factory=list)

    @property
    def author_display(self) -> str | None:
        """``updatedBy.display`` or ``None``."""
        return self.updated_by.display if self.updated_by else None


class ChangelogList(RootModel[list[ChangelogEntry]]):
    """A bare JSON array of changelog entries.

    Example:
        >>> ChangelogList.model_validate([{"id": "1"}]).root[0].id
        '1'
    """
