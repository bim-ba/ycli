"""Pydantic model for Tracker /myself (Me)."""

from __future__ import annotations

from ycli.yandex.account import Account
from ycli.yandex.models import APIModel


class Me(APIModel):
    """The authenticated Tracker user (``GET /v3/myself``) — a safe auth probe."""

    uid: int | None = None
    login: str | None = None
    display: str | None = None
    email: str | None = None

    def account(self) -> Account:
        """This user as an :class:`Account` (for ``auth status``)."""
        uid = None if self.uid is None else str(self.uid)
        return Account(uid=uid, login=self.login, email=self.email, display_name=self.display)
