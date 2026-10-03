"""Pydantic models for Tracker priorities (Priority + ItemList[Priority] + typed write bodies)."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel
from ycli.yandex.tracker.models import LocalizedName


class Priority(APIModel):
    """A priority reference (``/priorities`` item).

    The live v3 API carries the display name in ``name`` (``display`` stays null there), so
    both fields are mapped. Asked for with ``localized=False``, ``name`` is the name in every
    language instead of a string.

    Examples:
        >>> Priority.model_validate({"key": "normal", "name": "Normal"}).name
        'Normal'
    """

    key: str | None = None
    name: str | LocalizedName | None = Field(
        default=None,
        description="Name in the caller's language, or in every language when not localized.",
    )
    display: str | None = None


class PriorityCreate(APIModel):
    """Typed request body for ``POST /priorities/`` (create a priority).

    Examples:
        >>> PriorityCreate(key="one", name=LocalizedName(ru="Низкий"), order=60).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'key': 'one', 'name': {'ru': 'Низкий'}, 'order': 60}
    """

    key: str = Field(description="Key of the new priority.")
    name: LocalizedName = Field(description="Localized display name of the priority.")
    order: int | None = Field(
        default=None,
        description="Weight controlling the priority's display order in the interface.",
    )
    description: str | None = Field(default=None, description="Description of the priority.")


class PriorityUpdate(APIModel):
    """Typed request body for ``PATCH /priorities/{id}?version=`` (edit a priority).

    Only the fields that are set are sent, so omitted fields stay unchanged.

    Examples:
        >>> PriorityUpdate(description="Описание").model_dump(by_alias=True, exclude_none=True)
        {'description': 'Описание'}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the priority."
    )
    description: str | None = Field(default=None, description="New description of the priority.")
