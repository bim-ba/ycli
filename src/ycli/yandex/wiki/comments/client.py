"""Declarative Yandex Wiki /pages/{id}/comments client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""
import uplink

from ycli.yandex.wiki._base import WikiResource
from ycli.yandex.wiki.comments.models import CommentsResponse


class CommentsClient(WikiResource):
    """Declarative HTTP for ``/pages/{id}/comments``."""

    @uplink.returns.json()
    @uplink.get("pages/{page_id}/comments")
    def list(
        self,
        page_id: uplink.Path,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
    ) -> CommentsResponse:  # ty: ignore[empty-body]
        """``GET /pages/{id}/comments`` → comment listing.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.list(12345).results[0].author_display  # doctest: +SKIP
            'Сава Знатнов'
        """
