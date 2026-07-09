"""Declarative Tracker /queues client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.pagination import OffsetStrategy
from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.queues.models import Queue, QueueList

_PAGE_SIZE = 50


class QueuesClient(TrackerResource):
    """Declarative HTTP for ``/queues`` (page-paginated list + single get)."""

    @uplink.returns.json()
    @uplink.get("queues/")
    def _list_page(
        self,
        page: uplink.Query = 1,  # ty: ignore[invalid-parameter-default]
        per_page: uplink.Query("perPage") = _PAGE_SIZE,  # ty: ignore[invalid-type-form]
    ) -> QueueList:  # ty: ignore[empty-body]
        """One raw page of queues (1-based ``page``, size ``perPage``); internal — use ``list``."""

    def list(self, *, limit: int | None = None) -> QueueList:
        """``GET /queues/`` → flat :class:`QueueList`, draining ``page``/``perPage`` internally.

        Capped at ``limit`` (``None`` = every queue). The API returns 50 queues per page and
        pages via ``page``/``perPage``; this advances the page number until a short page comes
        back. Note the trailing slash — ``GET /queues/`` (without it Tracker returns the single
        queue whose key is empty).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.list(limit=10).root[0].key  # doctest: +SKIP
            'TEST'
        """
        strategy = OffsetStrategy(extract=lambda page: page.root, page_size=_PAGE_SIZE)
        queues = strategy.collect(
            lambda offset: self._list_page(page=offset // _PAGE_SIZE + 1, per_page=_PAGE_SIZE),
            limit,
        )
        return QueueList(queues)

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}")
    def get(
        self,
        queue_id: uplink.Path,
        expand: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> Queue:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}`` → a single :class:`Queue`.

        ``queue_id`` is the queue key (case-sensitive) or numeric id. Pass ``expand`` to include
        extra blocks, e.g. ``expand="all"`` (or ``projects,components,versions,types,team,
        workflows,fields,issueTypesConfig``).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.get(queue_id="TEST", expand="all").name  # doctest: +SKIP
            'Test'
        """
