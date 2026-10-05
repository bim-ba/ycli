"""Pydantic models for Tracker statuses (Status + ItemList[Status] + typed write bodies)."""

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.tracker.models import LocalizedName

#: The kind of an issue status: where in the life of an issue it stands.
StatusType = Literal["new", "inProgress", "paused", "done", "cancelled"] | str


class Status(APIModel):
    """An issue status (``/statuses`` item) — the workflow stage an issue is in.

    Examples:
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


class StatusCreate(RequestBody):
    """Typed request body for ``POST /statuses/`` (create an issue status).

    Examples:
        >>> StatusCreate(key="myStatus", name=LocalizedName(ru="Мой"), type="paused").model_dump(
        ...     exclude_none=True
        ... )
        {'key': 'myStatus', 'name': {'ru': 'Мой'}, 'type': 'paused'}
    """

    key: str = Field(
        description="Key of the new status: Latin letters, starting with a lower-case letter."
    )
    name: LocalizedName = Field(description="Localized display name of the status.")
    type: StatusType = Field(description="Status type.")


class StatusUpdate(RequestBody):
    """Typed request body for ``PATCH /statuses/{id}?version=`` (edit a status).

    Only the fields that are set are sent, so omitted fields stay unchanged.

    Examples:
        >>> StatusUpdate(order=350).model_dump(exclude_none=True)
        {'order': 350}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the status."
    )
    description: str | None = Field(default=None, description="New description of the status.")
    order: int | None = Field(
        default=None, description="New weight controlling the status' display order."
    )
    type: StatusType | None = Field(
        default=None,
        description="New status type.",
    )
