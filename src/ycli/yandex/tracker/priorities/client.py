"""Declarative Tracker priorities client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""
import uplink

from ycli.yandex.tracker._base import TrackerResource
from ycli.yandex.tracker.priorities.models import PriorityList


class PrioritiesClient(TrackerResource):
    """Declarative HTTP for ``/priorities``."""

    @uplink.returns.json()
    @uplink.get("priorities")
    def list(self) -> PriorityList:  # ty: ignore[empty-body]
        """``GET /priorities`` → priority listing.

        Example:
            >>> client = TrackerClient.from_env()  # doctest: +SKIP
            >>> client.priorities.list().root[0].key  # doctest: +SKIP
            'normal'
        """
