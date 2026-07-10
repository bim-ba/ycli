"""Pydantic models for Tracker issue remote links (links to external-application objects)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class RemoteLinkType(APIModel):
    """The ``type`` sub-object of a remote link — the link-type and its directional names.

    Example:
        >>> RemoteLinkType.model_validate({"id": "relates", "outward": "Relates"}).id
        'relates'
    """

    id: str | None = Field(default=None, description="Link-type identifier, e.g. ``relates``.")
    inward: str | None = Field(default=None, description="Link-type name in the inward direction.")
    outward: str | None = Field(
        default=None, description="Link-type name in the outward direction."
    )


class RemoteApplication(APIModel):
    """The ``application`` sub-object — the external app the linked object belongs to.

    Example:
        >>> RemoteApplication.model_validate({"id": "1", "name": "test-app"}).name
        'test-app'
    """

    id: str | None = Field(default=None, description="External application identifier.")
    type: str | None = Field(default=None, description="Application type, e.g. ``app``.")
    name: str | None = Field(default=None, description="Display name of the external application.")


class RemoteObject(APIModel):
    """The ``object`` sub-object — the linked object inside the external application.

    Example:
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

    Example:
        >>> RemoteLink.model_validate(
        ...     {"id": 51, "type": {"id": "relates"}, "object": {"key": "TEST-17"}}
        ... ).object_key
        'TEST-17'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of this remote link."
    )
    id: int | str | None = Field(default=None, description="Identifier of the remote link.")
    type: RemoteLinkType | None = Field(default=None, description="The link type.")
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


class RemoteLinkList(RootModel[list[RemoteLink]]):
    """A bare JSON array of remote links — public return type of ``RemoteLinksClient.list``.

    Example:
        >>> RemoteLinkList.model_validate([{"direction": "outward"}]).root[0].direction
        'outward'
    """


class RemoteLinkCreate(APIModel):
    """Typed request body for ``POST /issues/{key}/remotelinks`` (add an external link).

    Example:
        >>> RemoteLinkCreate(key="TEST-17", origin="ru.yandex.bitbucket").model_dump(
        ...     exclude_none=True
        ... )
        {'relationship': 'RELATES', 'key': 'TEST-17', 'origin': 'ru.yandex.bitbucket'}
    """

    relationship: str = Field(
        default="RELATES", description="Link type; ``RELATES`` (related) is recommended."
    )
    key: str = Field(description="Key of the object in the external application.")
    origin: str = Field(description="Identifier of the external application to link with.")
