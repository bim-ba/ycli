"""Pydantic models for Tracker resolutions (Resolution + ResolutionList + write bodies)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel
from ycli.yandex.tracker.models import LocalizedName


class Resolution(APIModel):
    """An issue resolution (``/resolutions`` item) — the outcome recorded when an issue closes.

    Examples:
        >>> Resolution.model_validate({"id": 1, "key": "fixed", "name": "Решен"}).key
        'fixed'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the resolution.",
    )
    id: int | None = Field(
        default=None, description="Unique identifier of the resolution in Tracker."
    )
    key: str | None = Field(default=None, description="Key of the resolution.")
    version: int | None = Field(default=None, description="Version of the resolution.")
    name: str | None = Field(default=None, description="Display name of the resolution.")
    description: str | None = Field(default=None, description="Description of the resolution.")
    order: int | None = Field(
        default=None,
        description="Weight controlling the resolution's display order in the interface.",
    )


class ResolutionList(RootModel[list[Resolution]]):
    """A bare JSON array of resolutions.

    Examples:
        >>> ResolutionList.model_validate([{"key": "fixed"}]).root[0].key
        'fixed'
    """


class ResolutionCreate(APIModel):
    """Typed request body for ``POST /resolutions/`` (create a resolution).

    Examples:
        >>> ResolutionCreate(key="wontFix", name=LocalizedName(ru="Отклонено")).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'key': 'wontFix', 'name': {'ru': 'Отклонено'}}
    """

    key: str = Field(
        description="Key of the new resolution: Latin letters, starting with a lower-case letter."
    )
    name: LocalizedName = Field(description="Localized display name of the resolution.")


class ResolutionUpdate(APIModel):
    """Typed request body for ``PATCH /resolutions/{id}?version=`` (edit a resolution).

    Only the fields that are set are sent, so omitted fields stay unchanged.

    Examples:
        >>> ResolutionUpdate(order=90).model_dump(by_alias=True, exclude_none=True)
        {'order': 90}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the resolution."
    )
    description: str | None = Field(default=None, description="New description of the resolution.")
    order: int | None = Field(
        default=None, description="New weight controlling the resolution's display order."
    )
