"""Pydantic models for Tracker statuses (Status + StatusList)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class Status(APIModel):
    """An issue status (``/statuses`` item) — the workflow stage an issue is in.

    Example:
        >>> Status.model_validate({"id": 1, "key": "open", "name": "Открыт"}).key
        'open'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the status.",
    )
    id: int | None = Field(
        default=None, description="Unique identifier of the issue status in Tracker."
    )
    version: int | None = Field(default=None, description="Version of the issue status.")
    key: str | None = Field(default=None, description="Key of the issue status.")
    name: str | None = Field(default=None, description="Display name of the issue status.")
    description: str | None = Field(default=None, description="Description of the issue status.")
    order: int | None = Field(
        default=None, description="Weight controlling the status' display order in the interface."
    )
    type: str | None = Field(
        default=None,
        description="Status type: one of new, inProgress, paused, done, cancelled.",
    )


class StatusList(RootModel[list[Status]]):
    """A bare JSON array of statuses.

    Example:
        >>> StatusList.model_validate([{"key": "open"}]).root[0].key
        'open'
    """
