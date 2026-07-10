"""Declarative Yandex Wiki /pages/{id}/resources client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import uplink

from ycli.yandex.pagination import CursorStrategy
from ycli.yandex.wiki.base import WikiResource
from ycli.yandex.wiki.resources.models import ResourceItemList, ResourcesResponse


class ResourcesClient(WikiResource):
    """Declarative HTTP for ``/pages/{id}/resources`` (unified attachments + grids)."""

    @uplink.returns.json()
    @uplink.get("pages/{page_id}/resources")
    def _list_page(
        self,
        page_id: uplink.Path,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
        cursor: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        q: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        types: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        order_by: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> ResourcesResponse:  # ty: ignore[empty-body]
        """One raw page of resource envelopes + ``next_cursor`` (internal; callers use ``list``)."""

    def list(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        q: str | None = None,
        types: str | None = None,
        order_by: str | None = None,
    ) -> ResourceItemList:
        """``GET /pages/{id}/resources`` → flat :class:`ResourceItemList`, draining ``next_cursor``.

        The unified listing of everything attached to a page — attachments AND grids — as
        ``{type, item}`` envelopes. Capped at ``limit`` (``None`` = every resource); narrow
        with ``q`` (title search), ``types`` (comma-separated ``attachment,grid``), and
        ``order_by`` (``name_title`` or ``created_at``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.resources.list(12345, types="attachment").root[0].type  # doctest: +SKIP
            'attachment'
        """
        strategy = CursorStrategy(
            extract=lambda page: page.results,
            next_of=lambda page: page.next_cursor,
        )
        resources = strategy.collect(
            lambda cursor: self._list_page(
                page_id, page_size=100, cursor=cursor, q=q, types=types, order_by=order_by
            ),
            limit,
        )
        return ResourceItemList(resources)
