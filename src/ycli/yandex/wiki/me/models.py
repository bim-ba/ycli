"""Pydantic models for Wiki /users/me (the authenticated user)."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel
from ycli.yandex.wiki.models import UserIdentity


class Organization(APIModel):
    """The organization ids the user belongs to (``dir_id``, ``collab_id``)."""

    dir_id: str | None = Field(default=None, description="Id of the Yandex 360 organization.")
    collab_id: str | None = Field(default=None, description="Id of the meta-organization.")


class Me(APIModel):
    """The authenticated Wiki user (``GET /v1/users/me``) — a safe auth probe."""

    username: str | None = Field(default=None, description="Login of the user.")
    home_cluster: str | None = Field(default=None, description="Home cluster of the user.")
    identity: UserIdentity | None = Field(default=None, description="Passport and cloud uids.")
    org: Organization | None = Field(default=None, description="Organization of the user.")
