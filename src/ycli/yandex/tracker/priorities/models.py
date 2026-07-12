"""Pydantic models for Tracker priorities (Priority + PriorityList + typed write bodies)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class Priority(APIModel):
    """A priority reference (``/priorities`` item).

    The live v3 API carries the display name in ``name`` (``display`` stays null there), so
    both fields are mapped.

    Example:
        >>> Priority.model_validate({"key": "normal", "name": "Normal"}).name
        'Normal'
    """

    key: str | None = None
    name: str | None = None
    display: str | None = None


class PriorityList(RootModel[list[Priority]]):
    """A bare JSON array of priorities.

    Example:
        >>> PriorityList.model_validate([{"key": "normal"}]).root[0].key
        'normal'
    """


class LocalizedName(APIModel):
    """A localized display name (the ``name`` object) — Russian and/or English text.

    Example:
        >>> LocalizedName(ru="Низкий", en="Low").model_dump(exclude_none=True)
        {'ru': 'Низкий', 'en': 'Low'}
    """

    ru: str | None = Field(default=None, description="Name in Russian.")
    en: str | None = Field(default=None, description="Name in English.")


class PriorityCreate(APIModel):
    """Typed request body for ``POST /priorities/`` (create a priority).

    Example:
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

    Example:
        >>> PriorityUpdate(description="Описание").model_dump(by_alias=True, exclude_none=True)
        {'description': 'Описание'}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the priority."
    )
    description: str | None = Field(default=None, description="New description of the priority.")
