"""Declarative Tracker filters client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.filters.models import Filter


class FiltersClient(TrackerResource):
    """Declarative HTTP for ``/filters``."""

    @uplink.returns.json()
    @uplink.get("filters/{filter_id}")
    def get(self, filter_id: uplink.Path) -> Filter:  # ty: ignore[empty-body]
        """``GET /filters/{filter_id}`` → parameters of one saved filter.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filters.get(filter_id="12345").name  # doctest: +SKIP
            'My open issues'
        """
