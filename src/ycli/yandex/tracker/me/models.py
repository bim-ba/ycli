"""Pydantic model for Tracker /myself (Me)."""

from pydantic import Field

from ycli.yandex.models import APIModel


class Me(APIModel):
    """The authenticated Tracker user (``GET /v3/myself``) — a safe auth probe."""

    uid: int | None = Field(default=None, description="Tracker account identifier of the user.")
    login: str | None = Field(default=None, description="User login.")
    display: str | None = Field(default=None, description="Display name of the user.")
    email: str | None = Field(default=None, description="User email address.")
