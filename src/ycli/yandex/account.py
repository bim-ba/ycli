"""``Account`` — who a token belongs to, in the same shape for every service."""

from __future__ import annotations

from ycli.yandex.models import APIModel


class Account(APIModel):
    """The common subset of every service's ``me`` payload; each ``me`` model maps itself here.

    Example:
        >>> Account(login="alice").login
        'alice'
    """

    uid: str | None = None
    login: str | None = None
    email: str | None = None
    display_name: str | None = None
