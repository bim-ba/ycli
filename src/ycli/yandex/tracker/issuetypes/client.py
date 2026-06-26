"""Declarative Tracker issue-types client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""
import uplink

from ycli.yandex.tracker._base import TrackerResource
from ycli.yandex.tracker.issuetypes.models import IssueTypeList


class IssueTypesClient(TrackerResource):
    """Declarative HTTP for ``/issuetypes``."""

    @uplink.timeout(30)
    @uplink.returns.json()
    @uplink.get("issuetypes")
    def list(self) -> IssueTypeList:  # ty: ignore[empty-body]
        """``GET /issuetypes`` → issue-type listing.

        Example:
            >>> client = TrackerClient.from_env()  # doctest: +SKIP
            >>> client.issuetypes.list().root[0].key  # doctest: +SKIP
            'bug'
        """
