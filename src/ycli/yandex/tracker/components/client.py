"""Declarative Tracker components client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.components.models import ComponentList


class ComponentsClient(TrackerResource):
    """Declarative HTTP for ``/components``."""

    @uplink.returns.json()
    @uplink.get("components")
    def list(self) -> ComponentList:  # ty: ignore[empty-body]
        """``GET /components`` → all components created by the organisation's users.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.list().root[0].name  # doctest: +SKIP
            'Test'
        """
