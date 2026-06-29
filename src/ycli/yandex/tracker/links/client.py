"""Declarative Tracker issue-links client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker._base import TrackerResource
from ycli.yandex.tracker.links.models import Link, LinkList


class LinksClient(TrackerResource):
    """Declarative HTTP for ``/issues/{key}/links``."""

    @uplink.returns.json()
    @uplink.get("issues/{key}/links")
    def list(self, key: uplink.Path) -> LinkList:  # ty: ignore[empty-body]
        """``GET /issues/{key}/links`` → link listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.links.list(key="DATAENGINEERING-130").root[0].object_key  # doctest: +SKIP
            'DATAENGINEERING-129'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{key}/links")
    def add(self, key: uplink.Path, body: uplink.Body) -> Link:  # ty: ignore[empty-body]
        """``POST /issues/{key}/links`` — link two issues. Returns the link.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.links.add(
            ...     "DATAENGINEERING-130",
            ...     {"relationship": "depends on", "issue": "DATAENGINEERING-129"},
            ... ).object_key  # doctest: +SKIP
            'DATAENGINEERING-129'
        """
