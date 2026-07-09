"""Declarative Yandex Wiki /pages/{id}/attachments client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import uplink

from ycli.yandex.pagination import CursorStrategy
from ycli.yandex.wiki.attachments.models import AttachmentList, AttachmentsResponse
from ycli.yandex.wiki.base import WikiResource


class AttachmentsClient(WikiResource):
    """Declarative HTTP for ``/pages/{id}/attachments``."""

    @uplink.returns.json()
    @uplink.get("pages/{page_id}/attachments")
    def _list_page(
        self,
        page_id: uplink.Path,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
        cursor: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> AttachmentsResponse:  # ty: ignore[empty-body]
        """One raw page of attachments + ``next_cursor`` (internal; callers use ``list``)."""

    def list(self, page_id: int, *, limit: int | None = None) -> AttachmentList:
        """``GET /pages/{id}/attachments`` → flat :class:`AttachmentList`, draining ``next_cursor``.

        Capped at ``limit`` (``None`` = every attachment).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.list(12345, limit=50).root[0].name  # doctest: +SKIP
            'diagram.png'
        """
        strategy = CursorStrategy(
            extract=lambda page: page.results,
            next_of=lambda page: page.next_cursor,
        )
        attachments = strategy.collect(
            lambda cursor: self._list_page(page_id, page_size=100, cursor=cursor),
            limit,
        )
        return AttachmentList(attachments)
