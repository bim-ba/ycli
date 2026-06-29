"""Declarative Tracker link-types client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.linktypes.models import LinkTypeList


class LinkTypesClient(TrackerResource):
    """Declarative HTTP for ``/linktypes``."""

    @uplink.returns.json()
    @uplink.get("linktypes")
    def list(self) -> LinkTypeList:  # ty: ignore[empty-body]
        """``GET /linktypes`` → link-type listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.linktypes.list().root[0].id  # doctest: +SKIP
            'relates'
        """
