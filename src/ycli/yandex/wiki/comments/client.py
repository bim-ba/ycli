"""Declarative Yandex Wiki /pages/{id}/comments client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import uplink

from ycli.yandex.pagination import CursorStrategy
from ycli.yandex.wiki.base import WikiResource
from ycli.yandex.wiki.comments.models import CommentList, CommentsResponse


class CommentsClient(WikiResource):
    """Declarative HTTP for ``/pages/{id}/comments``."""

    @uplink.returns.json()
    @uplink.get("pages/{page_id}/comments")
    def _list_page(
        self,
        page_id: uplink.Path,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
        cursor: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> CommentsResponse:  # ty: ignore[empty-body]
        """One raw page of comments + ``next_cursor`` (internal; callers use ``list``)."""

    def list(self, page_id: int, *, limit: int | None = None) -> CommentList:
        """``GET /pages/{id}/comments`` → flat :class:`CommentList`, draining ``next_cursor``.

        Capped at ``limit`` (``None`` = every comment).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.list(12345, limit=50).root[0].author  # doctest: +SKIP
            'Сава Знатнов'
        """
        strategy = CursorStrategy(
            extract=lambda page: page.results,
            next_of=lambda page: page.next_cursor,
        )
        comments = strategy.collect(
            lambda cursor: self._list_page(page_id, page_size=100, cursor=cursor),
            limit,
        )
        return CommentList(comments)
