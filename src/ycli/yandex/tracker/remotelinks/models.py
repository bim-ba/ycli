"""Pydantic models for Tracker issue remote links (links to external-application objects)."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import (
    APIModel,
    DisplayStr,
    RequestBody,  # pydantic resolves field types via get_type_hints() at runtime
)
from ycli.yandex.tracker.models import LinkType


class RemoteApplication(APIModel):
    """The ``application`` sub-object — the external app the linked object belongs to.

    Examples:
        >>> RemoteApplication.model_validate({"id": "1", "name": "test-app"}).name
        'test-app'
    """

    id: str | None = Field(default=None, description="External application identifier.")
    type: str | None = Field(default=None, description="Application type, e.g. ``app``.")
    name: str | None = Field(default=None, description="Display name of the external application.")


class RemoteObject(APIModel):
    """The ``object`` sub-object — the linked object inside the external application.

    Examples:
        >>> RemoteObject.model_validate({"key": "TEST-17"}).key
        'TEST-17'
    """

    id: str | None = Field(default=None, description="Identifier of the external object.")
    key: str | None = Field(default=None, description="Key of the external object.")
    application: RemoteApplication | None = Field(
        default=None, description="The external application the object belongs to."
    )


class RemoteLink(APIModel):
    """A link between a Tracker issue and an external-application object (``/remotelinks`` item).

    Examples:
        >>> RemoteLink.model_validate(
        ...     {"id": 51, "type": {"id": "relates"}, "object": {"key": "TEST-17"}}
        ... ).object_key
        'TEST-17'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of this remote link."
    )
    id: int | str | None = Field(default=None, description="Identifier of the remote link.")
    type: LinkType | None = Field(default=None, description="The link type.")
    direction: str | None = Field(
        default=None, description="Link direction (``outward`` / ``inward``) for asymmetric types."
    )
    object: RemoteObject | None = Field(
        default=None, description="The linked external-application object."
    )
    created_by: DisplayStr = Field(
        default=None, alias="createdBy", description="Display name of the link's creator."
    )
    updated_by: DisplayStr = Field(
        default=None,
        alias="updatedBy",
        description="Display name of the last user to edit the link.",
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last-update timestamp."
    )

    @property
    def object_key(self) -> str | None:
        """``object.key`` or ``None``."""
        return self.object.key if self.object else None


class RemoteLinkCreate(RequestBody):
    """Typed request body for ``POST /issues/{key}/remotelinks`` (add an external link).

    Examples:
        >>> RemoteLinkCreate(
        ...     relationship="RELATES", key="TEST-17", origin="ru.yandex.bitbucket"
        ... ).model_dump(exclude_none=True)
        {'relationship': 'RELATES', 'key': 'TEST-17', 'origin': 'ru.yandex.bitbucket'}
    """

    relationship: str = Field(description="Link type; ``RELATES`` (related) is recommended.")
    key: str = Field(description="Key of the object in the external application.")
    origin: str = Field(description="Identifier of the external application to link with.")
