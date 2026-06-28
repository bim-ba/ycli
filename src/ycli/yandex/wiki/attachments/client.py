"""Declarative Yandex Wiki /pages/{id}/attachments client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import uplink

from ycli.yandex.pagination import SinglePageStrategy
from ycli.yandex.wiki._base import WikiResource
from ycli.yandex.wiki.attachments.models import AttachmentList, AttachmentsResponse


class AttachmentsClient(WikiResource):
    """Declarative HTTP for ``/pages/{id}/attachments``."""

    @uplink.returns.json()
    @uplink.get("pages/{page_id}/attachments")
    def _list_page(
        self,
        page_id: uplink.Path,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
    ) -> AttachmentsResponse:  # ty: ignore[empty-body]
        """``GET /pages/{id}/attachments`` → raw ``AttachmentsResponse`` envelope (internal)."""

    def list(self, page_id: int, *, limit: int | None = None) -> AttachmentList:
        """``GET /pages/{id}/attachments`` → flat :class:`AttachmentList`.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.list(12345).root[0].name  # doctest: +SKIP
            'diagram.png'
        """
        items = SinglePageStrategy(extract=lambda page: page.results).collect(
            lambda cursor: self._list_page(page_id, page_size=100), limit
        )
        return AttachmentList(items)
