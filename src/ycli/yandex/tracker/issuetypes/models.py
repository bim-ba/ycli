"""Pydantic models for Tracker issue types (IssueType + ItemList[IssueType] + write bodies)."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.tracker.models import LocalizedName


class IssueType(APIModel):
    """An issue type descriptor (``/issuetypes`` item).

    The live v3 API carries the display name in ``name`` (``display`` stays null there), so
    both fields are mapped.

    Examples:
        >>> IssueType.model_validate({"key": "task", "name": "Task"}).name
        'Task'
    """

    key: str | None = None
    name: str | None = None
    display: str | None = None


class IssueTypeCreate(RequestBody):
    """Typed request body for ``POST /issuetypes/`` (create an issue type).

    Examples:
        >>> IssueTypeCreate(key="client", name=LocalizedName(ru="Клиент")).model_dump(
        ...     exclude_none=True
        ... )
        {'key': 'client', 'name': {'ru': 'Клиент'}}
    """

    key: str = Field(description="Key of the new issue type.")
    name: LocalizedName = Field(description="Localized display name of the issue type.")


class IssueTypeUpdate(RequestBody):
    """Typed request body for ``PATCH /issuetypes/{id}?version=`` (edit an issue type).

    Only the fields that are set are sent, so omitted fields stay unchanged.

    Examples:
        >>> IssueTypeUpdate(name=LocalizedName(ru="Покупатель")).model_dump(exclude_none=True)
        {'name': {'ru': 'Покупатель'}}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the issue type."
    )
