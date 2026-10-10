"""Tracker worklog client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.worklog import endpoints

if TYPE_CHECKING:
    from ycli.yandex.core.listing import Listing
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.worklog.models import (
        ImportWorklog,
        Worklog,
        WorklogCreate,
        WorklogSearch,
        WorklogUpdate,
    )


class WorklogClient(Resource):
    """An issue's worklog (relative-paginated) and its writes; org-wide search and listing."""

    def list(
        self, issue_key: str, *, limit: int | None = None, next: str | None = None
    ) -> Listing[Worklog]:
        """All worklog entries on an issue, draining the ``id=<last record id>`` cursor.

        ``GET /issues/{key}/worklog`` sorts by ascending record id and pages relatively:
        each next page repeats with ``id=<id of the last record seen>`` until a page comes
        back empty. Capped at ``limit`` (``None`` = every entry); a small cap narrows the page
        to ``limit`` rows.

        Args:
            issue_key: The issue's key.
            limit: The most entries to return; ``None`` returns every entry.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.

        Returns:
            The issue's worklog entries, ascending by record id.

        Examples:
            >>> [entry.duration for entry in tracker.worklog.list("DE-61", limit=500)]
            ['PT1H', 'PT2H', 'PT3H']
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_(issue_key, page_size=page_size)
        return self._session.iterate(paged, limit=limit, next=next)

    def search(self, body: WorklogSearch) -> ItemList[Worklog]:
        """``POST /worklog/_search`` → org-wide worklog entries matching the body filter.

        ``body`` is ``{"createdBy": …, "createdAt": {"from": …, "to": …}}`` (all optional).

        Args:
            body: The filter on ``createdBy`` and ``createdAt``.

        Returns:
            The matching worklog entries.

        Examples:
            >>> from ycli.yandex.tracker.worklog.models import WorklogSearch
            >>> found = tracker.worklog.search(
            ...     WorklogSearch.model_validate(
            ...         {
            ...             "createdBy": "veikus",
            ...             "createdAt": {
            ...                 "from": "2018-06-06T00:00:00",
            ...                 "to": "2018-06-07T00:00:00",
            ...             },
            ...         }
            ...     )
            ... )
            >>> found.root[0].duration
            'PT2H'
        """
        return self._session.send(endpoints.search(body))

    def list_global(
        self,
        created_by: str | None = None,
        created_from: str | None = None,
        created_to: str | None = None,
    ) -> ItemList[Worklog]:
        """``GET /worklog?createdBy=…&createdAt=from:…&createdAt=to:…`` → org-wide worklog.

        Distinct from :meth:`list`, which is scoped to a single issue.

        Args:
            created_by: Only entries created by this user.
            created_from: Only entries created at or after this time.
            created_to: Only entries created at or before this time.

        Returns:
            The organisation's matching worklog entries.

        Examples:
            >>> tracker.worklog.list_global(
            ...     created_by="alice", created_from="2019-01-01", created_to="2019-02-01"
            ... ).root[0].duration
            'P3W'
        """
        return self._session.send(endpoints.list_global(created_by, created_from, created_to))

    def create(self, issue_key: str, body: WorklogCreate) -> Worklog:
        """``POST /issues/{key}/worklog`` — log time spent. Returns the created entry.

        Args:
            issue_key: The issue's key.
            body: The entry's ``duration``, and optionally ``start`` and ``comment``.

        Returns:
            The created entry.

        Examples:
            >>> from ycli.yandex.tracker.worklog.models import WorklogCreate
            >>> tracker.worklog.create(
            ...     "DE-66",
            ...     WorklogCreate.model_validate(
            ...         {"duration": "PT2H", "start": "2021-03-04T10:00:00.000+0300"}
            ...     ),
            ... ).duration
            'PT2H'
        """
        return self._session.send(endpoints.create(issue_key, body))

    def update(self, issue_key: str, record_id: int | str, body: WorklogUpdate) -> Worklog:
        """``PATCH /issues/{key}/worklog/{record_id}`` — edit an entry. Returns it.

        Args:
            issue_key: The issue's key.
            record_id: The entry's id.
            body: The fields to change.

        Returns:
            The edited entry.

        Examples:
            >>> from ycli.yandex.tracker.worklog.models import WorklogUpdate
            >>> tracker.worklog.update(
            ...     "DE-67", "671", WorklogUpdate.model_validate({"duration": "PT45M"})
            ... ).duration
            'PT45M'
        """
        return self._session.send(endpoints.update(issue_key, record_id, body))

    def delete(self, issue_key: str, record_id: str) -> None:
        """Delete a worklog entry (``DELETE …/worklog/{id}`` → 204). Raises on non-2xx.

        Args:
            issue_key: The issue's key.
            record_id: The entry's id.

        Examples:
            >>> tracker.worklog.delete("DE-68", "681")
        """
        self._session.send(endpoints.delete(issue_key, record_id))

    def import_(self, issue_key: str, body: ImportWorklog) -> ItemList[Worklog]:
        """``POST /issues/{issue_key}/worklogs/_import`` — import a worklog (note plural path).

        Returns a ``ItemList[Worklog]`` — the live endpoint answers with a JSON **array** of the
        created worklog record(s), not a single object.

        Args:
            issue_key: The issue's key.
            body: The worklog fields, including the source ``createdAt`` and ``createdBy``.

        Returns:
            The created worklog record(s).

        Examples:
            >>> from ycli.yandex.tracker.worklog.models import ImportWorklog
            >>> tracker.worklog.import_(
            ...     "TEST-5",
            ...     ImportWorklog.model_validate(
            ...         {
            ...             "duration": "PT2H",
            ...             "createdAt": "2021-04-05T06:07:08.000+0000",
            ...             "createdBy": "15",
            ...             "start": "2021-04-05T09:00:00.000+0000",
            ...         }
            ...     ),
            ... ).root[0].duration
            'PT2H'
        """
        return self._session.send(endpoints.import_(issue_key, body))
