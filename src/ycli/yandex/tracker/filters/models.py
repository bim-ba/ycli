"""Pydantic models for Tracker saved filters (Filter + nested permission models)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel


class FilterFieldRef(APIModel):
    """A reference to an issue field shown in the filter UI (``fields`` / ``groupBy`` item).

    Example:
        >>> FilterFieldRef.model_validate({"id": "status", "display": "Status"}).id
        'status'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the field.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the field.")
    display: str | None = Field(default=None, description="Human-readable name of the field.")


class FilterUser(APIModel):
    """A user referenced by a filter's owner or permissions.

    Example:
        >>> FilterUser.model_validate({"id": "1", "display": "Ivan"}).display
        'Ivan'
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


class FilterGroup(APIModel):
    """A group referenced by a filter's permissions.

    Example:
        >>> FilterGroup.model_validate({"id": "5", "display": "Everyone"}).display
        'Everyone'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the group.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the group.")
    display: str | None = Field(default=None, description="Human-readable name of the group.")


class FilterPermissionEntry(APIModel):
    """The users, groups and roles granted one permission level (READ or WRITE).

    Example:
        >>> FilterPermissionEntry.model_validate({"users": [], "groups": [], "roles": []}).roles
        []
    """

    users: list[FilterUser] = Field(
        default_factory=list, description="Users granted this permission level."
    )
    groups: list[FilterGroup] = Field(
        default_factory=list, description="Groups granted this permission level."
    )
    roles: list[Any] = Field(
        default_factory=list, description="Roles granted this permission level."
    )


class FilterPermissions(APIModel):
    """The read/write access rights of a filter (the ``permissions`` object).

    Example:
        >>> FilterPermissions.model_validate({"READ": {"users": []}}).read.users
        []
    """

    read: FilterPermissionEntry | None = Field(
        default=None, alias="READ", description="Object with read access rights to the filter."
    )
    write: FilterPermissionEntry | None = Field(
        default=None, alias="WRITE", description="Object with edit access rights to the filter."
    )


class Filter(APIModel):
    """A saved issue filter (``/filters/{id}``) — stored filtering conditions and UI settings.

    Example:
        >>> Filter.model_validate({"id": 12345, "name": "My open issues"}).name
        'My open issues'
    """

    id: int | None = Field(default=None, description="Unique identifier of the filter.")
    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the filter.",
    )
    name: str | None = Field(default=None, description="Display name of the filter.")
    filter: dict[str, Any] | None = Field(
        default=None, description="Object with the filtering conditions."
    )
    query: str | None = Field(
        default=None, description="Filtering conditions written in the Tracker query language."
    )
    fields: list[FilterFieldRef] = Field(
        default_factory=list,
        description="Issue fields displayed in the Tracker UI when the filter is used.",
    )
    group_by: FilterFieldRef | None = Field(
        default=None,
        alias="groupBy",
        description="Field used to group results in the Tracker UI.",
    )
    favorite: bool | None = Field(
        default=None,
        description="Whether the filter is marked as a favourite (true) or not (false).",
    )
    permissions: FilterPermissions | None = Field(
        default=None, description="Object with the filter's access rights."
    )
    owner: FilterUser | None = Field(
        default=None, description="Object with information about the filter's owner."
    )
