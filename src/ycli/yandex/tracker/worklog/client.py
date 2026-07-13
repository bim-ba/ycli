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
    def _page(
        self,
        key: uplink.Path,
        per_page: uplink.Query("perPage") = 100,  # ty: ignore[invalid-type-form]
        record_id: uplink.Query("id") = None,  # ty: ignore[invalid-type-form]
    ) -> WorklogList:  # ty: ignore[empty-body]
        """One raw ``/issues/{key}/worklog`` page (a bare JSON array); callers use ``list``."""

    def list(self, key: str, *, limit: int | None = None) -> WorklogList:
        """All worklog entries on an issue, draining the ``id=<last record id>`` cursor.

        ``GET /issues/{key}/worklog`` sorts by ascending record id and pages relatively:
        each next page repeats with ``id=<id of the last record seen>`` until a page comes
        back empty. Capped at ``limit`` (``None`` = every entry).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.list(key="DATAENGINEERING-1").root[0].duration  # doctest: +SKIP
            'PT2H'
        """
        records = self._drain_relative(
            extract=lambda page: page.root,
            id_of=lambda record: str(record.id) if record.id is not None else None,
            fetch_page=lambda cursor, per_page: self._page(
                key, per_page=per_page, record_id=cursor
            ),
            limit=limit,
        )
        return WorklogList(records)

    @uplink.returns.json()
    @uplink.json
    @uplink.post("worklog/_search")
    def search(self, body: uplink.Body) -> WorklogList:  # ty: ignore[empty-body]
        """``POST /worklog/_search`` → org-wide worklog entries matching the body filter.

        ``body`` is ``{"createdBy": …, "createdAt": {"from": …, "to": …}}`` (all optional).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.search({"createdBy": "veikus"}).root[0].duration  # doctest: +SKIP
            'PT2H'
        """

    @uplink.returns.json()
    @uplink.get("worklog")
    def global_list(
        self,
        created_by: uplink.Query("createdBy") = None,  # ty: ignore[invalid-type-form]
        created_at: uplink.Query("createdAt") = None,  # ty: ignore[invalid-type-form]
    ) -> WorklogList:  # ty: ignore[empty-body]
        """``GET /worklog?createdBy=…&createdAt=from:…&createdAt=to:…`` → org-wide worklog.

        ``created_at`` is a list of ``from:<ts>`` / ``to:<ts>`` strings (repeated ``createdAt``
        query params). Distinct from :meth:`list`, which is scoped to a single issue.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.global_list(
            ...     created_by="veikus", created_at=["from:2018-06-06", "to:2018-06-07"]
            ... ).root[0].duration  # doctest: +SKIP
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
