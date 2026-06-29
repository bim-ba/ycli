"""Declarative Yandex Wiki /pages/{id}/comments client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import uplink

from ycli.yandex.pagination import SinglePageStrategy
from ycli.yandex.wiki._base import WikiResource
from ycli.yandex.wiki.comments.models import CommentList, CommentsResponse


class CommentsClient(WikiResource):
    """Declarative HTTP for ``/pages/{id}/comments``."""

    @uplink.returns.json()
    @uplink.get("pages/{page_id}/comments")
    def _list_page(
        self,
        page_id: uplink.Path,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
    ) -> CommentsResponse:  # ty: ignore[empty-body]
        """``GET /pages/{id}/comments`` → raw ``CommentsResponse`` envelope (internal)."""

    def list(self, page_id: int, *, limit: int | None = None) -> CommentList:
        """``GET /pages/{id}/comments`` → flat :class:`CommentList`.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.list(12345).root[0].author_display  # doctest: +SKIP
            'Сава Знатнов'
        """
        return SinglePageStrategy.collect_wrapped(
            lambda cursor: self._list_page(page_id, page_size=100),
            extract=lambda page: page.results,
            wrap=CommentList,
            limit=limit,
        )
