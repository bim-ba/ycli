"""Pydantic models for Wiki /users/me (the authenticated user)."""

from __future__ import annotations

from ycli.yandex.models import APIModel


class Identity(APIModel):
    uid: str | None = None
    cloud_uid: str | None = None


class Organization(APIModel):
    dir_id: str | None = None
    collab_id: str | None = None


class Me(APIModel):
    """The authenticated Wiki user (``GET /v1/users/me``) — a safe auth probe."""

    username: str | None = None
    home_cluster: str | None = None
    identity: Identity | None = None
    org: Organization | None = None
