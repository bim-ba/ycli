"""Declarative Tracker issue-comments client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.comments.models import Comment, CommentList


class CommentsClient(TrackerResource):
    """Declarative HTTP for ``/issues/{key}/comments``."""

    @uplink.returns.json()
    @uplink.get("issues/{key}/comments")
    def _page(
        self,
        key: uplink.Path,
        per_page: uplink.Query("perPage") = 100,  # ty: ignore[invalid-type-form]
        comment_id: uplink.Query("id") = None,  # ty: ignore[invalid-type-form]
    ) -> CommentList:  # ty: ignore[empty-body]
        """One raw ``/issues/{key}/comments`` page (a bare JSON array); callers use ``list``."""

    def list(self, key: str, *, limit: int | None = None) -> CommentList:
        """All comments on an issue, draining the ``id=<last comment id>`` relative cursor.

        ``GET /issues/{key}/comments`` returns one page at a time (50 comments by default);
        each next page repeats with ``id=<id of the last comment seen>`` until a page comes
        back empty. Capped at ``limit`` (``None`` = every comment).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.list(key="DATAENGINEERING-1").root[0].created_by  # doctest: +SKIP
            'Сава Знатнов'
        """
        comments = self._drain_relative(
            extract=lambda page: page.root,
            id_of=lambda comment: str(comment.id) if comment.id is not None else None,
            fetch_page=lambda cursor, per_page: self._page(
                key, per_page=per_page, comment_id=cursor
            ),
            limit=limit,
        )
        return CommentList(comments)

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

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("issues/{key}/comments/{comment_id}")
    def edit(self, key: uplink.Path, comment_id: uplink.Path, body: uplink.Body) -> Comment:  # ty: ignore[empty-body]
        """``PATCH /issues/{key}/comments/{comment_id}`` — edit a comment. Returns it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.edit(
            ...     "DATAENGINEERING-1", 2238, {"text": "fixed"}
            ... ).text  # doctest: +SKIP
            'fixed'
        """

    @uplink.delete("issues/{key}/comments/{comment_id}")
    def _delete(self, key: uplink.Path, comment_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /issues/{key}/comments/{comment_id}`` (204, no body; internal)."""

    def delete(self, key: str, comment_id: str) -> None:
        """Delete a comment (``DELETE …/comments/{id}`` → 204). Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.delete("DATAENGINEERING-1", 2238)  # doctest: +SKIP
        """
        self._delete(key, comment_id)

    @uplink.returns.json()
    @uplink.post("issues/{key}/comments/{comment_id}/reactions/{name}")
    def react(self, key: uplink.Path, comment_id: uplink.Path, name: uplink.Path) -> Comment:  # ty: ignore[empty-body]
        """``POST …/comments/{comment_id}/reactions/{name}`` — add a reaction. Returns the comment.

        ``name`` is an uppercase reaction key (LIKE, DISLIKE, HEART, ROCKET, FIRE, …).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.react("DATAENGINEERING-1", 2238, "LIKE").id  # doctest: +SKIP
            2238
        """
