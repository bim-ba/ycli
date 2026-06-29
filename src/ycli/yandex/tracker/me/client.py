"""Declarative Tracker /myself client (uplink) — transport ONLY."""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.me.models import Me


class MeClient(TrackerResource):
    """Declarative HTTP for ``/myself``."""

    @uplink.returns.json()
    @uplink.get("myself")
    def get(self) -> Me:  # ty: ignore[empty-body]
        """``GET /myself`` → the authenticated ``Me`` (a safe auth probe)."""
