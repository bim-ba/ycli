"""Declarative Wiki /users/me client (uplink) — transport ONLY."""
import uplink

from ycli.yandex.wiki._base import WikiResource
from ycli.yandex.wiki.me.models import Me


class MeClient(WikiResource):
    """Declarative HTTP for ``/users/me``."""

    @uplink.returns.json()
    @uplink.get("users/me")
    def get(self) -> Me:  # ty: ignore[empty-body]
        """``GET /users/me`` → the authenticated ``Me`` (a safe auth probe)."""
