"""Tracker ``/issues`` client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.issues.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.errors import YandexInvalidRequestError
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.issues import endpoints
from ycli.yandex.tracker.issues.models import (
    ImportTask,
    Issue,
    IssueCreate,
    IssueSearch,
    IssueUpdate,
    ScrollClear,
)

if TYPE_CHECKING:
    from ycli.yandex.tracker.bulk.models import (
        BulkChange,
        BulkMove,
        BulkTransition,
        BulkUpdate,
    )


class IssuesClient(Resource):
    """Get, search (paginated), count, create, update, move and suggest Tracker issues."""

    def get(
        self,
        issue_key: str,
        *,
        expand: str | None = None,
        fields: str | None = None,
    ) -> Issue:
        """``GET /issues/{key}`` → a single ``Issue``.

        Args:
            issue_key: The issue's key.
            expand: The extra blocks to include: ``transitions``, ``attachments``, ``comments``.
            fields: The comma-separated issue fields to include in the reply.

        Returns:
            The issue.

        Examples:
            >>> tracker.issues.get("DE-7").summary
            'Fix the login page'
        """
        return self._session.send(endpoints.get(issue_key, expand=expand, fields=fields))

    def search(
        self,
        body: IssueSearch,
        *,
        limit: int | None = None,
        expand: str | None = None,
        scroll_type: str | None = None,
        per_scroll: int | None = None,
        scroll_ttl_millis: int | None = None,
    ) -> ItemList[Issue]:
        """``POST /issues/_search`` → every matching issue, page by page, at most ``limit``.

        ``body`` is ``{"filter": …}`` or ``{"query": …}``. ``limit=None`` fetches every page (up
        to Tracker's 10 000 results); when the cap leaves issues behind, a warning is logged to
        ``ycli.http``. ``scroll_type`` reads the results by scrolling instead, which has no such
        cap.

        Args:
            body: The search body, ``{"filter": …}`` or ``{"query": …}``.
            limit: The most issues to return; ``None`` fetches every page.
            expand: The extra blocks to include: ``transitions``, ``attachments``, ``comments``.
            scroll_type: ``sorted`` (the order of the search) or ``unsorted`` to scroll through
                the results instead of paging by number.
            per_scroll: The issues a scroll page holds (1000 at most; the API's default is 100).
            scroll_ttl_millis: How long the scroll stays open between requests, in milliseconds.

        Returns:
            The matching issues.

        Raises:
            YandexInvalidRequestError: If ``limit`` is below 1.

        Examples:
            >>> from ycli.yandex.tracker.issues.models import IssueSearch
            >>> found = tracker.issues.search(
            ...     IssueSearch.model_validate({"filter": {"queue": "DE", "status": "open"}}),
            ...     limit=500,
            ... )
            >>> found.root[0].key
            'DE-7'
        """
        if limit is not None and limit < 1:
            raise YandexInvalidRequestError(
                f"limit must be a positive number of issues or None, got {limit}"
            )
        # A small cap needs no 100-issue page.
        page_size = min(limit, endpoints.SEARCH_PAGE_SIZE) if limit else endpoints.SEARCH_PAGE_SIZE
        if scroll_type is not None:
            paged = endpoints.search_scroll(
                body,
                expand=expand,
                scroll_type=scroll_type,
                per_scroll=per_scroll,
                scroll_ttl_millis=scroll_ttl_millis,
            )
        else:
            paged = endpoints.search(body, expand=expand, page_size=page_size)
        return ItemList[Issue](list(self._session.iterate(paged, limit=limit)))

    def count(self, body: IssueSearch) -> int:
        """``POST /issues/_count`` → the number of matching issues.

        Args:
            body: The search body, ``{"filter": …}`` or ``{"query": …}``.

        Returns:
            The number of matching issues.
        """
        return self._session.send(endpoints.count(body))

    def create(
        self,
        body: IssueCreate,
        *,
        notify: bool | None = None,
    ) -> Issue:
        """``POST /issues/`` — create from a ready body; returns the created ``Issue``.

        Args:
            body: The issue fields.
            notify: Whether to notify the users in the issues' fields; ``None`` leaves the API's
                default (it notifies).

        Returns:
            The created issue.
        """
        return self._session.send(endpoints.create(body, notify=notify))

    def update(self, issue_key: str, body: IssueUpdate) -> Issue:
        """``PATCH /issues/{key}`` — update fields; returns the updated ``Issue``.

        Args:
            issue_key: The issue's key.
            body: The fields to change.

        Returns:
            The updated issue.
        """
        return self._session.send(endpoints.update(issue_key, body))

    def move(
        self,
        issue_key: str,
        queue: str,
        *,
        expand: str | None = None,
        initial_status: bool | None = None,
        move_all_fields: bool | None = None,
        notify: bool | None = None,
        notify_author: bool | None = None,
    ) -> Issue:
        """``POST /issues/{key}/_move?queue=<key>`` — returns the moved ``Issue`` (new key).

        Args:
            issue_key: The issue's key.
            queue: The key of the queue to move the issue to.
            expand: The extra blocks to include: ``attachments``, ``comments``, ``workflow``,
                ``transitions``.
            initial_status: Whether to reset the status to the new queue's initial one; needed when
                the queues have different workflows.
            move_all_fields: Whether to keep the versions, components and projects the new queue
                also has; the API clears them by default.
            notify: Whether to notify the users in the issues' fields; ``None`` leaves the API's
                default (it notifies).
            notify_author: Whether to notify the author of the change; ``None`` leaves the API's
                default (it does not).

        Returns:
            The moved issue.
        """
        return self._session.send(
            endpoints.move(
                issue_key,
                queue,
                expand=expand,
                initial_status=initial_status,
                move_all_fields=move_all_fields,
                notify=notify,
                notify_author=notify_author,
            )
        )

    def suggest(
        self,
        text: str,
        *,
        queue: str | None = None,
        full: bool | None = None,
        fields: str | None = None,
        expand: str | None = None,
        embed: str | None = None,
    ) -> ItemList[Issue]:
        """``GET /issues/_suggest?input=<text>`` → issues whose summary contains ``text``.

        Args:
            text: The text to look for in issue summaries.
            queue: The key of the queue to search in.
            full: Whether to return each issue in full; ``fields``, ``expand`` and ``embed``
                need it.
            fields: The comma-separated issue fields to include (with ``full``).
            expand: The extra blocks to include (with ``full``).
            embed: The blocks named in ``expand`` to return in more detail (with ``full``).

        Returns:
            The matching issues.
        """
        return self._session.send(
            endpoints.suggest(
                text, queue=queue, full=full, fields=fields, expand=expand, embed=embed
            )
        )

    def scroll_clear(self, body: ScrollClear) -> None:
        """Release a search scroll's server resources (``POST …/scroll/_clear``).

        Args:
            body: The scroll ids mapped to their scroll tokens.
        """
        self._session.send(endpoints.scroll_clear(body))

    def update_bulk(
        self,
        body: BulkUpdate,
        *,
        notify: bool | None = None,
    ) -> BulkChange:
        """``POST /bulkchange/_update`` — mass-edit issues. Returns the started ``BulkChange``.

        Args:
            body: The request body: the issues to change and the field values to set.
            notify: Whether to notify the users in the issues' fields; ``None`` leaves the API's
                default (it notifies).

        Returns:
            The started bulk change.

        Examples:
            >>> from ycli.yandex.tracker.bulk.models import BulkUpdate
            >>> tracker.issues.update_bulk(
            ...     BulkUpdate.model_validate(
            ...         {"issues": ["DE-1", "DE-2"], "values": {"priority": "minor"}}
            ...     )
            ... ).status
            'CREATED'
        """
        return self._session.send(endpoints.update_bulk(body, notify=notify))

    def move_bulk(
        self,
        body: BulkMove,
        *,
        notify: bool | None = None,
    ) -> BulkChange:
        """``POST /bulkchange/_move`` — mass-move issues to another queue. Returns a ``BulkChange``.

        Args:
            body: The request body: the target queue and the issues to move.
            notify: Whether to notify the users in the issues' fields; ``None`` leaves the API's
                default (it notifies).

        Returns:
            The started bulk change.

        Examples:
            >>> from ycli.yandex.tracker.bulk.models import BulkMove
            >>> tracker.issues.move_bulk(
            ...     BulkMove.model_validate({"queue": "CHECK", "issues": ["DE-3"]})
            ... ).id
            '2cd'
        """
        return self._session.send(endpoints.move_bulk(body, notify=notify))

    def transition_bulk(
        self,
        body: BulkTransition,
        *,
        notify: bool | None = None,
    ) -> BulkChange:
        """``POST /bulkchange/_transition`` — mass status transition. Returns a ``BulkChange``.

        Args:
            body: The request body: the transition to run and the issues to run it on.
            notify: Whether to notify the users in the issues' fields; ``None`` leaves the API's
                default (it notifies).

        Returns:
            The started bulk change.

        Examples:
            >>> from ycli.yandex.tracker.bulk.models import BulkTransition
            >>> tracker.issues.transition_bulk(
            ...     BulkTransition.model_validate({"transition": "close", "issues": ["DE-4"]})
            ... ).status
            'CREATED'
        """
        return self._session.send(endpoints.transition_bulk(body, notify=notify))

    def import_(self, body: ImportTask) -> Issue:
        """``POST /issues/_import`` — import an issue preserving its history. Returns the ``Issue``.

        Args:
            body: The issue fields, including the source ``createdAt`` and ``createdBy``.

        Returns:
            The imported issue.

        Examples:
            >>> from ycli.yandex.tracker.issues.models import ImportTask
            >>> tracker.issues.import_(
            ...     ImportTask.model_validate(
            ...         {
            ...             "queue": "TEST",
            ...             "summary": "Old task",
            ...             "createdAt": "2017-08-29T12:34:41.740+0000",
            ...             "createdBy": "11",
            ...             "key": "TEST-41",
            ...         }
            ...     )
            ... ).key
            'TEST-41'
        """
        return self._session.send(endpoints.import_(body))
