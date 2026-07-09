"""Pydantic models for Tracker components (Component + ComponentList)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class ComponentQueue(APIModel):
    """The queue a component belongs to (the ``queue`` object).

    Example:
        >>> ComponentQueue.model_validate({"key": "ORG", "display": "My queue"}).key
        'ORG'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the queue.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the queue.")
    key: str | None = Field(default=None, description="Key of the queue.")
    display: str | None = Field(default=None, description="Human-readable name of the queue.")


class ComponentLead(APIModel):
    """The owner (lead) of a component (the ``lead`` object).

    Example:
        >>> ComponentLead.model_validate({"id": "11", "display": "Ivan Ivanov"}).display
        'Ivan Ivanov'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the user.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the user.")
    display: str | None = Field(default=None, description="Display name of the user.")
    cloud_uid: str | None = Field(
        default=None,
        alias="cloudUid",
        description="Unique identifier of the user in Yandex Cloud Organization.",
    )
    passport_uid: int | None = Field(
        default=None,
        alias="passportUid",
        description="Unique identifier of the account in Yandex 360 for Business and Yandex ID.",
    )


class Component(APIModel):
    """A queue component (``/components`` item) — a sub-area used to classify issues.

    Example:
        >>> Component.model_validate({"id": 1, "name": "Test"}).name
        'Test'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the component.",
    )
    id: int | None = Field(default=None, description="Unique identifier of the component.")
    version: int | None = Field(
        default=None,
        description="Version of the component; each change increments the version number.",
    )
    name: str | None = Field(default=None, description="Display name of the component.")
    queue: ComponentQueue | None = Field(
        default=None, description="Object with information about the component's queue."
    )
    description: str | None = Field(default=None, description="Text description of the component.")
    lead: ComponentLead | None = Field(
        default=None, description="Object with information about the component's owner."
    )
    assign_auto: bool | None = Field(
        default=None,
        alias="assignAuto",
        description="Whether the owner is auto-assigned to new issues carrying this component.",
    )


class ComponentList(RootModel[list[Component]]):
    """A bare JSON array of components — the flat public shape of ``components.list()``.

    Example:
        >>> ComponentList.model_validate([{"name": "Test"}]).root[0].name
        'Test'
    """
