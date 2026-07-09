"""Declarative Tracker statuses client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.statuses.models import StatusList


class StatusesClient(TrackerResource):
    """Declarative HTTP for ``/statuses``."""

    @uplink.returns.json()
    @uplink.get("statuses")
    def list(self) -> StatusList:  # ty: ignore[empty-body]
        """``GET /statuses`` → status listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.statuses.list().root[0].key  # doctest: +SKIP
            'open'
        """
