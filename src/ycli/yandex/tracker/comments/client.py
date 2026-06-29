"""Declarative Tracker issue-comments client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.comments.models import Comment, CommentList


class CommentsClient(TrackerResource):
    """Declarative HTTP for ``/issues/{key}/comments``."""

    @uplink.returns.json()
    @uplink.get("issues/{key}/comments")
    def list(self, key: uplink.Path) -> CommentList:  # ty: ignore[empty-body]
        """``GET /issues/{key}/comments`` → comment listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.list(key="DATAENGINEERING-1").root[0].created_by  # doctest: +SKIP
            'Сава Знатнов'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{key}/comments/")
    def add(self, key: uplink.Path, body: uplink.Body) -> Comment:  # ty: ignore[empty-body]
        """``POST /issues/{key}/comments/`` — add a comment. Returns it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.add("DATAENGINEERING-1", {"text": "Готово ✅"}).id  # doctest: +SKIP
            2238
        """
