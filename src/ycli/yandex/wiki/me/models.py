"""Pydantic models for Wiki /users/me (the authenticated user)."""

from __future__ import annotations

from ycli.yandex.models import APIModel
from ycli.yandex.wiki.models import UserIdentity


class Organization(APIModel):
    """The organization ids the user belongs to (``dir_id``, ``collab_id``)."""

    dir_id: str | None = None
    collab_id: str | None = None


class Me(APIModel):
    """The authenticated Wiki user (``GET /v1/users/me``) — a safe auth probe."""

    username: str | None = None
    home_cluster: str | None = None
    identity: UserIdentity | None = None
    org: Organization | None = None
