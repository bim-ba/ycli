"""Pydantic model for Tracker /myself (Me)."""

from __future__ import annotations

from ycli.yandex.models import APIModel


class Me(APIModel):
    """The authenticated Tracker user (``GET /v3/myself``) — a safe auth probe."""

    uid: int | None = None
    login: str | None = None
    display: str | None = None
    email: str | None = None
