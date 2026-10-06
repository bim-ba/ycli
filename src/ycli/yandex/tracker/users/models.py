"""Pydantic models for Tracker users (User and the relative-page envelope)."""

from pydantic import Field

from ycli.yandex.models import APIModel

# ``User`` lives with the models several resources share: an absence carries one too.
from ycli.yandex.tracker.models import User as User


class UsersRelativeResponse(APIModel):
    """Internal envelope of one ``/users/_relative`` page (``{users, hasNext}``).

    Examples:
        >>> UsersRelativeResponse.model_validate({"users": [{"uid": 1}], "hasNext": True}).has_next
        True
    """

    users: list[User] = Field(
        default_factory=list, description="Users on this page, sorted by ascending uid."
    )
    has_next: bool | None = Field(
        default=None,
        alias="hasNext",
        description="Whether further pages remain (true) or this is the last page (false).",
    )
