"""Tracker worklog client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.worklog import endpoints
from ycli.yandex.tracker.worklog.models import Worklog

if TYPE_CHECKING:
    from collections.abc import Sequence


class WorklogClient(Resource):
    """An issue's worklog (relative-paginated) and its writes; org-wide search and listing."""

    def list(self, key: str, *, limit: int | None = None) -> ItemList[Worklog]:
        """All worklog entries on an issue, draining the ``id=<last record id>`` cursor.

        ``GET /issues/{key}/worklog`` sorts by ascending record id and pages relatively:
        each next page repeats with ``id=<id of the last record seen>`` until a page comes
        back empty. Capped at ``limit`` (``None`` = every entry); a small cap narrows the page
        to ``limit`` rows.

        Args:
            key: The issue's key.
            limit: The most entries to return; ``None`` returns every entry.

        Returns:
            The issue's worklog entries, ascending by record id.

        Examples:
            >>> [entry.duration for entry in tracker.worklog.list("DE-61", limit=500).root]
            ['PT1H', 'PT2H', 'PT3H']
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_worklog(key, page_size=page_size)
        return ItemList[Worklog](list(self._session.iterate(paged, limit=limit)))

    def search(self, body: dict[str, Any]) -> ItemList[Worklog]:
        """``POST /worklog/_search`` → org-wide worklog entries matching the body filter.

        ``body`` is ``{"createdBy": …, "createdAt": {"from": …, "to": …}}`` (all optional).

        Args:
            body: The filter on ``createdBy`` and ``createdAt``.

        Returns:
            The matching worklog entries.

        Examples:
            >>> found = tracker.worklog.search(
            ...     {
            ...         "createdBy": "veikus",
            ...         "createdAt": {"from": "2018-06-06T00:00:00", "to": "2018-06-07T00:00:00"},
            ...     }
            ... )
            >>> found.root[0].duration
            'PT2H'
        """
        return self._session.send(endpoints.search_worklog(body))

    def global_list(
        self, created_by: str | None = None, created_at: Sequence[str] | str | None = None
    ) -> ItemList[Worklog]:
        """``GET /worklog?createdBy=…&createdAt=from:…&createdAt=to:…`` → org-wide worklog.

        ``created_at`` is a list of ``from:<ts>`` / ``to:<ts>`` strings (repeated ``createdAt``
        query params). Distinct from :meth:`list`, which is scoped to a single issue.

        Args:
            created_by: Only entries created by this user.
            created_at: ``from:<ts>`` / ``to:<ts>`` strings bounding the creation time.

        Returns:
            The organisation's matching worklog entries.

        Examples:
            >>> tracker.worklog.global_list(
            ...     created_by="alice", created_at=["from:2019-01-01", "to:2019-02-01"]
            ... ).root[0].duration
            'P3W'
        """
        return self._session.send(endpoints.list_global_worklog(created_by, created_at))

    def create(self, key: str, body: dict[str, Any]) -> Worklog:
        """``POST /issues/{key}/worklog`` — log time spent. Returns the created entry.

        Args:
            key: The issue's key.
            body: The entry's ``duration``, and optionally ``start`` and ``comment``.

        Returns:
            The created entry.

        Examples:
            >>> tracker.worklog.create("DE-66", {"duration": "PT2H", "comment": "pairing"}).duration
            'PT2H'
        """
        return self._session.send(endpoints.create_worklog(key, body))

    def edit(self, key: str, record_id: int | str, body: dict[str, Any]) -> Worklog:
        """``PATCH /issues/{key}/worklog/{record_id}`` — edit an entry. Returns it.

        Args:
            key: The issue's key.
            record_id: The entry's id.
            body: The fields to change.

        Returns:
            The edited entry.

        Examples:
            >>> tracker.worklog.edit("DE-67", "671", {"duration": "PT45M"}).duration
            'PT45M'
        """
        return self._session.send(endpoints.edit_worklog(key, record_id, body))

    def delete(self, key: str, record_id: str) -> None:
        """Delete a worklog entry (``DELETE …/worklog/{id}`` → 204). Raises on non-2xx.

        Args:
            key: The issue's key.
            record_id: The entry's id.

        Examples:
            >>> tracker.worklog.delete("DE-68", "681")
        """
        self._session.send(endpoints.delete_worklog(key, record_id))
