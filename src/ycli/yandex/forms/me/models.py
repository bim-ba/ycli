"""Pydantic model for Forms /users/me (User)."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel


class User(APIModel):
    """The authenticated user (``GET /v1/users/me``) — a safe auth probe.

    Examples:
        >>> User.model_validate({"id": 1, "uid": "u", "cloud_uid": "c", "email": "e@x"}).email
        'e@x'
    """

    id: int | None = Field(default=None, description="Forms' numeric id of the user.")
    uid: str | None = Field(default=None, description="Passport uid of the user.")
    cloud_uid: str | None = Field(default=None, description="Cloud uid of the user.")
    login: str | None = Field(default=None, description="Login of the user.")
    display: str | None = Field(default=None, description="Name to show for the user.")
    email: str | None = Field(default=None, description="Email of the user.")
