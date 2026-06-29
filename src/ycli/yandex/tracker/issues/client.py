"""Declarative Tracker /issues client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import uplink

from ycli.yandex.tracker._base import TrackerResource
from ycli.yandex.tracker.issues.models import Issue, IssueList


class IssuesClient(TrackerResource):
    """Declarative HTTP for ``/issues`` (get, search, count, create, update)."""

    @uplink.returns.json()
    @uplink.get("issues/{key}")
    def get(self, key: uplink.Path) -> Issue:  # ty: ignore[empty-body]
        """``GET /issues/{key}`` → a single ``Issue`` (raises on non-2xx).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issues.get(key="DATAENGINEERING-1").status  # doctest: +SKIP
            'inProgress'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/_search")
    def search(self, body: uplink.Body) -> IssueList:  # ty: ignore[empty-body]
        """``POST /issues/_search`` → list of issues.

        ``body`` is ``{"filter": …}`` or ``{"query": …}``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issues.search({"query": "Queue: DATAENGINEERING"}).root[
            ...     0
            ... ].key  # doctest: +SKIP
            'DATAENGINEERING-1'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/_count")
    def count(self, body: uplink.Body) -> int:  # ty: ignore[empty-body]
        """``POST /issues/_count`` → a bare integer count.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issues.count({"filter": {"queue": "DATAENGINEERING"}})  # doctest: +SKIP
            137
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/")
    def create(self, body: uplink.Body) -> Issue:  # ty: ignore[empty-body]
        """``POST /issues/`` — create from a ready body. Returns the created ``Issue``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issues.create(
            ...     {"queue": "DATAENGINEERING", "summary": "New", "type": {"key": "improvement"}}
            ... ).key  # doctest: +SKIP
            'DATAENGINEERING-200'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("issues/{key}")
    def update(self, key: uplink.Path, body: uplink.Body) -> Issue:  # ty: ignore[empty-body]
        """``PATCH /issues/{key}`` — update fields. Returns the updated ``Issue``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.issues.update(
            ...     key="DATAENGINEERING-1", body={"priority": {"key": "critical"}}
            ... ).priority  # doctest: +SKIP
            'critical'
        """
