"""Pydantic models for Tracker components (Component + ItemList[Component])."""

from typing import Annotated

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.sync.marks import Identity
from ycli.yandex.tracker.models import AccessPermissions, KeyedReference, Reference, UserReference


class Component(APIModel):
    """A queue component (``/components`` item) — a sub-area used to classify issues.

    Examples:
        >>> Component.model_validate({"id": 1, "name": "Test"}).name
        'Test'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the component.",
    )
    id: Annotated[int | None, Identity()] = Field(
        default=None, description="Unique identifier of the component."
    )
    version: int | None = Field(
        default=None,
        description="Version of the component; each change increments the version number.",
    )
    name: str | None = Field(default=None, description="Display name of the component.")
    queue: KeyedReference | None = Field(
        default=None, description="Object with information about the component's queue."
    )
    description: str | None = Field(default=None, description="Text description of the component.")
    lead: UserReference | None = Field(
        default=None, description="Object with information about the component's owner."
    )
    assign_auto: bool | None = Field(
        default=None,
        alias="assignAuto",
        description="Whether the owner is auto-assigned to new issues carrying this component.",
    )


class ComponentCreate(RequestBody):
    """Typed request body for ``POST /components`` (create a component).

    Examples:
        >>> ComponentCreate(name="UI", queue="TEST").model_dump(exclude_none=True)
        {'name': 'UI', 'queue': 'TEST'}
    """

    name: str = Field(description="Display name of the new component.")
    queue: str = Field(description="Key of the queue the component is created in.")
    description: str | None = Field(default=None, description="Text description of the component.")
    lead: str | None = Field(default=None, description="Login of the component's owner (lead).")
    assign_auto: bool | None = Field(
        default=None,
        serialization_alias="assignAuto",
        description="Whether the owner is auto-assigned to new issues carrying this component.",
    )


class ComponentUpdate(RequestBody):
    """Typed request body for ``PATCH /components/{id}?version=`` (edit a component).

    Only the fields that are set are sent, so omitted fields stay unchanged.

    Examples:
        >>> ComponentUpdate(assign_auto=True).model_dump(exclude_none=True)
        {'assignAuto': True}
    """

    name: str | None = Field(default=None, description="New display name of the component.")
    description: str | None = Field(
        default=None, description="New text description of the component."
    )
    lead: str | None = Field(default=None, description="New login of the component's owner (lead).")
    assign_auto: bool | None = Field(
        default=None,
        serialization_alias="assignAuto",
        description="Whether the owner is auto-assigned to new issues carrying this component.",
    )


class ComponentUserAccess(APIModel):
    """One user's rights on a component (``GET /components/{id}/permissions/users/{userId}``).

    Examples:
        >>> ComponentUserAccess.model_validate({"component": {"id": 1}}).component.id
        1
    """

    user: UserReference | None = Field(default=None, description="The user the rights belong to.")
    component: Component | None = Field(default=None, description="The component.")
    permissions: AccessPermissions | None = Field(
        default=None,
        description="Rights by kind (create, read, write, deny), with who grants each.",
    )


class ComponentGroupAccess(APIModel):
    """One group's rights on a component (``GET /components/{id}/permissions/groups/{groupId}``).

    Examples:
        >>> ComponentGroupAccess.model_validate({"group": {"id": "5"}}).group.id
        '5'
    """

    group: Reference | None = Field(default=None, description="The group the rights belong to.")
    component: Component | None = Field(default=None, description="The component.")
    permissions: AccessPermissions | None = Field(
        default=None,
        description="Rights by kind (create, read, write, deny), with who grants each.",
    )
