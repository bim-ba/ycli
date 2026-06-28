"""Pydantic model for Forms /users/me (User)."""

from __future__ import annotations

from ycli.yandex.models import APIModel


class User(APIModel):
    """The authenticated user (``GET /v1/users/me``) — a safe auth probe.

    Example:
        >>> User.model_validate({"id": 1, "uid": "u", "cloud_uid": "c", "email": "e@x"}).email
        'e@x'
    """

    id: int | None = None
    uid: str | None = None
    cloud_uid: str | None = None
    email: str | None = None
