"""Pydantic models for Tracker external applications (Application + ItemList[Application])."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel


class Application(APIModel):
    """An external application that issues can be linked to (``/applications`` item).

    Examples:
        >>> Application.model_validate({"id": "my-app", "name": "My app"}).id
        'my-app'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the application.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the application.")
    type: str | None = Field(
        default=None, description="Type of the application; matches the value of the id parameter."
    )
    name: str | None = Field(default=None, description="Display name of the application.")
