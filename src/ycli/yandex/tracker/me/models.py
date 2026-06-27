"""Pydantic model for Tracker /myself (Me)."""
from __future__ import annotations

from pydantic import BaseModel


class Me(BaseModel):
    """The authenticated Tracker user (``GET /v3/myself``) — a safe auth probe."""

    uid: int | None = None
    login: str | None = None
    display: str | None = None
    email: str | None = None
