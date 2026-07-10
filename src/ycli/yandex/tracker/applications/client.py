"""Declarative Tracker external-applications client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.applications.models import ApplicationList
from ycli.yandex.tracker.base import TrackerResource


class ApplicationsClient(TrackerResource):
    """Declarative HTTP for ``/applications``."""

    @uplink.returns.json()
    @uplink.get("applications")
    def list(self) -> ApplicationList:  # ty: ignore[empty-body]
        """``GET /applications`` → external applications that issues can be linked to.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.applications.list().root[0].id  # doctest: +SKIP
            'my-application'
        """
