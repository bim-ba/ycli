"""Declarative Tracker worklog client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.worklog.models import Worklog, WorklogList


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

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{key}/worklog")
    def create(self, key: uplink.Path, body: uplink.Body) -> Worklog:  # ty: ignore[empty-body]
        """``POST /issues/{key}/worklog`` — log time spent. Returns the created entry.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.create(
            ...     "DATAENGINEERING-1", {"duration": "PT2H"}
            ... ).duration  # doctest: +SKIP
            'PT2H'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("issues/{key}/worklog/{record_id}")
    def edit(self, key: uplink.Path, record_id: uplink.Path, body: uplink.Body) -> Worklog:  # ty: ignore[empty-body]
        """``PATCH /issues/{key}/worklog/{record_id}`` — edit an entry. Returns it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.edit(
            ...     "DATAENGINEERING-1", 1, {"duration": "PT30M"}
            ... ).duration  # doctest: +SKIP
            'PT30M'
        """

    @uplink.delete("issues/{key}/worklog/{record_id}")
    def _delete(self, key: uplink.Path, record_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /issues/{key}/worklog/{record_id}`` (204, no body; internal)."""

    def delete(self, key: str, record_id: str) -> None:
        """Delete a worklog entry (``DELETE …/worklog/{id}`` → 204). Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.delete("DATAENGINEERING-1", 1)  # doctest: +SKIP
        """
        self._delete(key, record_id)
