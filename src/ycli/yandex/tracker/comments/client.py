"""Tracker issue ``/comments`` client on the httpx2 core."""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.comments import endpoints
from ycli.yandex.tracker.comments.models import Comment, CommentList


class CommentsClient(Resource):
    """List (relative-paginated), get, add, edit, delete and react to an issue's comments."""

    def list(self, key: str, *, limit: int | None = None) -> CommentList:
        """All comments on an issue, draining the ``id=<last comment id>`` relative cursor.

        ``GET /issues/{key}/comments`` returns one page at a time; each next page repeats with
        ``id=<id of the last comment seen>`` until a page comes back empty. Capped at ``limit``
        (``None`` = every comment); a small cap narrows the page to ``limit`` rows.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.list(key="DATAENGINEERING-1").root[0].created_by  # doctest: +SKIP
            'Сава Знатнов'
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_comments(key, page_size=page_size)
        return CommentList(list(self._session.iterate(paged, limit=limit)))

    def get(self, key: str, comment_id: int | str, *, expand: str | None = None) -> Comment:
        """``GET /issues/{key}/comments/{comment_id}`` — one comment. Returns it.

        ``comment_id`` is the numeric ``id`` or the string ``longId``. ``expand`` adds
        ``attachments``, ``html`` or ``all`` extra fields.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.get(
            ...     "DATAENGINEERING-1", 2238, expand="html"
            ... ).text_html  # doctest: +SKIP
            '<p>Готово</p>'
        """
        return self._session.send(endpoints.get_comment(key, comment_id, expand=expand))

    def add(self, key: str, body: dict[str, Any]) -> Comment:
        """``POST /issues/{key}/comments/`` — add a comment. Returns it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.add("DATAENGINEERING-1", {"text": "Готово ✅"}).id  # doctest: +SKIP
            2238
        """
        return self._session.send(endpoints.add_comment(key, body))

    def edit(self, key: str, comment_id: int | str, body: dict[str, Any]) -> Comment:
        """``PATCH /issues/{key}/comments/{comment_id}`` — edit a comment. Returns it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.edit(
            ...     "DATAENGINEERING-1", 2238, {"text": "fixed"}
            ... ).text  # doctest: +SKIP
            'fixed'
        """
        return self._session.send(endpoints.edit_comment(key, comment_id, body))

    def delete(self, key: str, comment_id: str) -> None:
        """Delete a comment (``DELETE …/comments/{id}`` → 204). Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.delete("DATAENGINEERING-1", 2238)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_comment(key, comment_id))

    def react(self, key: str, comment_id: int | str, name: str) -> Comment:
        """``POST …/comments/{comment_id}/reactions/{name}`` — add a reaction. Returns the comment.

        ``name`` is an uppercase reaction key (LIKE, DISLIKE, HEART, ROCKET, FIRE, …).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.react("DATAENGINEERING-1", 2238, "LIKE").id  # doctest: +SKIP
            2238
        """
        return self._session.send(endpoints.react_to_comment(key, comment_id, name))
