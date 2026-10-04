"""Pydantic models for the Tracker changelog (ChangeField + ChangelogEntry)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
    IDStr,
)


class ChangeField(APIModel):
    """One changed field within a ``ChangelogEntry``.

    ``from``/``to`` are polymorphic (string, object, array, or null depending on the
    field that changed) — typed ``Any`` and passed through verbatim.

    Examples:
        >>> ChangeField.model_validate({"field": {"id": "status"}, "to": {"key": "open"}}).field
        'status'
    """

    field: IDStr = Field(
        default=None, description="Identifier of the changed issue field, e.g. ``status``."
    )
    from_: Any = Field(
        default=None,
        alias="from",
        description="Value before the change (string, object, array or null).",
    )
    to: Any = Field(
        default=None,
        description="Value after the change (string, object, array or null).",
    )


class ChangelogEntry(APIModel):
    """A changelog event (``/issues/{key}/changelog`` item).

    Examples:
        >>> ChangelogEntry.model_validate(
        ...     {"id": "1", "updatedBy": {"display": "Сава"}, "fields": []}
        ... ).updated_by
        'Сава'
    """

    id: str | None = Field(default=None, description="Identifier of the change.")
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="When the issue was changed (ISO 8601)."
    )
    updated_by: DisplayStr = Field(
        default=None, alias="updatedBy", description="Display name of the user who made the change."
    )
    type: str | None = Field(
        default=None, description="Type of the change, e.g. ``IssueUpdated`` or ``IssueCreated``."
    )
    fields: list[ChangeField] = Field(
        default_factory=list, description="The issue fields changed by this event."
    )
