"""Declarative Tracker worklog client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""
import uplink

from ycli.yandex.tracker._base import TrackerResource
from ycli.yandex.tracker.worklog.models import WorklogList


class WorklogClient(TrackerResource):
    """Declarative HTTP for ``/issues/{key}/worklog``."""

    @uplink.returns.json()
    @uplink.get("issues/{key}/worklog")
    def list(self, key: uplink.Path) -> WorklogList:  # ty: ignore[empty-body]
        """``GET /issues/{key}/worklog`` → worklog listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.list(key="DATAENGINEERING-1").root[0].duration  # doctest: +SKIP
            'PT2H'
        """
