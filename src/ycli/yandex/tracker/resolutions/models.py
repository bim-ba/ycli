"""Pydantic models for Tracker resolutions (Resolution + ResolutionList)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class Resolution(APIModel):
    """An issue resolution (``/resolutions`` item) — the outcome recorded when an issue closes.

    Example:
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

    Example:
        >>> ResolutionList.model_validate([{"key": "fixed"}]).root[0].key
        'fixed'
    """
