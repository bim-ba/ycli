"""Pydantic models for Tracker saved filters (Filter + nested permission models)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel
from ycli.yandex.tracker.models import Reference, UserReference


class FilterPermissionEntry(APIModel):
    """The users, groups and roles granted one permission level (READ or WRITE).

    Examples:
        >>> FilterPermissionEntry.model_validate({"users": [], "groups": [], "roles": []}).roles
        []
    """

    users: list[UserReference] = Field(
        default_factory=list, description="Users granted this permission level."
    )
    groups: list[Reference] = Field(
        default_factory=list, description="Groups granted this permission level."
    )
    roles: list[Any] = Field(
        default_factory=list, description="Roles granted this permission level."
    )


class FilterPermissions(APIModel):
    """The read/write access rights of a filter (the ``permissions`` object).

    Examples:
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

    Examples:
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
    fields: list[Reference] = Field(
        default_factory=list,
        description="Issue fields displayed in the Tracker UI when the filter is used.",
    )
    group_by: Reference | None = Field(
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
    owner: UserReference | None = Field(
        default=None, description="Object with information about the filter's owner."
    )


class FilterCreate(APIModel):
    """Typed request body for ``POST /filters/`` (create a saved filter).

    Pass either ``filter`` (a field→condition mapping) or ``query`` (a Tracker query string),
    not both.

    Examples:
        >>> FilterCreate(name="My open", filter={"status": "open"}).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'name': 'My open', 'filter': {'status': 'open'}}
    """

    name: str = Field(description="Display name of the new filter.")
    filter: dict[str, Any] | None = Field(
        default=None, description="Filtering conditions as a field→condition mapping."
    )
    query: str | None = Field(
        default=None, description="Filtering conditions written in the Tracker query language."
    )


class FilterUpdate(APIModel):
    """Typed request body for ``PATCH /filters/{id}`` (edit a saved filter).

    Only the fields that are set are sent; note the API replaces ``filter`` wholesale rather
    than merging it, so pass every condition you want to keep.

    Examples:
        >>> FilterUpdate(name="Renamed").model_dump(by_alias=True, exclude_none=True)
        {'name': 'Renamed'}
    """

    name: str | None = Field(default=None, description="New display name of the filter.")
    filter: dict[str, Any] | None = Field(
        default=None, description="Replacement filtering conditions (replaces the whole object)."
    )
    query: str | None = Field(
        default=None, description="New filtering conditions in the Tracker query language."
    )


FilterFieldRef = Reference  # deprecated, removed in 0.38
FilterGroup = Reference  # deprecated, removed in 0.38
FilterUser = UserReference  # deprecated, removed in 0.38
