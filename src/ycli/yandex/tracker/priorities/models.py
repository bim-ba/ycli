"""Pydantic models for Tracker priorities (Priority + ItemList[Priority] + typed write bodies)."""

from typing import Annotated

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.sync.marks import Identity
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

    key: Annotated[str | None, Identity()] = Field(
        default=None, description="Key of the priority, e.g. ``normal``."
    )
    name: str | LocalizedName | None = Field(
        default=None,
        description="Name in the caller's language, or in every language when not localized.",
    )
    display: str | None = Field(
        default=None,
        description="Display name of the priority; null in the live v3 API, which uses ``name``.",
    )
    self_url: str | None = Field(
        default=None, alias="self", description="API resource URL of the priority."
    )
    id: int | str | None = Field(default=None, description="Identifier of the priority.")
    version: int | None = Field(default=None, description="Version of the priority.")
    description: str | None = Field(default=None, description="Description of the priority.")
    order: int | None = Field(
        default=None, description="Weight of the priority: its place in the list in the interface."
    )


class PriorityCreate(RequestBody):
    """Typed request body for ``POST /priorities/`` (create a priority).

    Examples:
        >>> PriorityCreate(key="one", name=LocalizedName(ru="Низкий"), order=60).model_dump(
        ...     exclude_none=True
        ... )
        {'key': 'one', 'name': {'ru': 'Низкий'}, 'order': 60}
    """

    key: str = Field(description="Key of the new priority.")
    name: LocalizedName = Field(description="Localized display name of the priority.")
    order: int = Field(
        description="Weight controlling the priority's display order in the interface. "
        "The API refuses a priority without it (measured).",
    )
    description: str | None = Field(default=None, description="Description of the priority.")


class PriorityUpdate(RequestBody):
    """Typed request body for ``PATCH /priorities/{id}?version=`` (edit a priority).

    Only the fields that are set are sent, so omitted fields stay unchanged.

    Examples:
        >>> PriorityUpdate(description="Описание").model_dump(exclude_none=True)
        {'description': 'Описание'}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the priority."
    )
    description: str | None = Field(default=None, description="New description of the priority.")
