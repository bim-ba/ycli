"""Declarative Tracker resolutions client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.resolutions.models import ResolutionList


class ResolutionsClient(TrackerResource):
    """Declarative HTTP for ``/resolutions``."""

    @uplink.returns.json()
    @uplink.get("resolutions")
    def list(self) -> ResolutionList:  # ty: ignore[empty-body]
        """``GET /resolutions`` → resolution listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.resolutions.list().root[0].key  # doctest: +SKIP
            'fixed'
        """
