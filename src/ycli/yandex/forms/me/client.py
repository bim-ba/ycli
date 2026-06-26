"""Declarative Forms /users/me client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""
import uplink

from ycli.yandex.forms._base import FormsResource
from ycli.yandex.forms.me.models import User


class MeClient(FormsResource):
    """Declarative HTTP for ``/users/me``."""

    @uplink.timeout(30)
    @uplink.returns.json()
    @uplink.get("users/me")
    def get(self) -> User:  # ty: ignore[empty-body]
        """``GET /users/me`` → the authenticated ``User`` (a safe auth probe).

        Example:
            >>> client = FormsClient.from_env()  # doctest: +SKIP
            >>> client.me.get().email  # doctest: +SKIP
            'znatnov.s@example.com'
        """
