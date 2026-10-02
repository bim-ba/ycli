"""Tracker worklog client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.worklog import endpoints
from ycli.yandex.tracker.worklog.models import Worklog, WorklogList

if TYPE_CHECKING:
    from collections.abc import Sequence


class WorklogClient(Resource):
    """An issue's worklog (relative-paginated) and its writes; org-wide search and listing."""

    def list(self, key: str, *, limit: int | None = None) -> WorklogList:
        """All worklog entries on an issue, draining the ``id=<last record id>`` cursor.

        ``GET /issues/{key}/worklog`` sorts by ascending record id and pages relatively:
        each next page repeats with ``id=<id of the last record seen>`` until a page comes
        back empty. Capped at ``limit`` (``None`` = every entry); a small cap narrows the page
        to ``limit`` rows.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.list(key="DATAENGINEERING-1").root[0].duration  # doctest: +SKIP
            'PT2H'
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_worklog(key, page_size=page_size)
        return WorklogList(list(self._session.iterate(paged, limit=limit)))

    def search(self, body: dict[str, Any]) -> WorklogList:
        """``POST /worklog/_search`` → org-wide worklog entries matching the body filter.

        ``body`` is ``{"createdBy": …, "createdAt": {"from": …, "to": …}}`` (all optional).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.search({"createdBy": "veikus"}).root[0].duration  # doctest: +SKIP
            'PT2H'
        """
        return self._session.send(endpoints.search_worklog(body))

    def global_list(
        self, created_by: str | None = None, created_at: Sequence[str] | str | None = None
    ) -> WorklogList:
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
        return self._session.send(endpoints.list_global_worklog(created_by, created_at))

    def create(self, key: str, body: dict[str, Any]) -> Worklog:
        """``POST /issues/{key}/worklog`` — log time spent. Returns the created entry.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.create(
            ...     "DATAENGINEERING-1", {"duration": "PT2H"}
            ... ).duration  # doctest: +SKIP
            'PT2H'
        """
        return self._session.send(endpoints.create_worklog(key, body))

    def edit(self, key: str, record_id: int | str, body: dict[str, Any]) -> Worklog:
        """``PATCH /issues/{key}/worklog/{record_id}`` — edit an entry. Returns it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.edit(
            ...     "DATAENGINEERING-1", 1, {"duration": "PT30M"}
            ... ).duration  # doctest: +SKIP
            'PT30M'
        """
        return self._session.send(endpoints.edit_worklog(key, record_id, body))

    def delete(self, key: str, record_id: str) -> None:
        """Delete a worklog entry (``DELETE …/worklog/{id}`` → 204). Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.worklog.delete("DATAENGINEERING-1", 1)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_worklog(key, record_id))
