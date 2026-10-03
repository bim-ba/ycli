"""Tracker issue ``/comments`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.comments import endpoints
from ycli.yandex.tracker.comments.models import Comment, CommentUpdate

if TYPE_CHECKING:
    from ycli.yandex.tracker.models import CommentCreate


class CommentsClient(Resource):
    """List (relative-paginated), get, add, edit, delete and react to an issue's comments."""

    def list(
        self,
        key: str,
        *,
        limit: int | None = None,
        expand: str | None = None,
    ) -> ItemList[Comment]:
        """All comments on an issue, draining the ``id=<last comment id>`` relative cursor.

        ``GET /issues/{key}/comments`` returns one page at a time; each next page repeats with
        ``id=<id of the last comment seen>`` until a page comes back empty. Capped at ``limit``
        (``None`` = every comment); a small cap narrows the page to ``limit`` rows.

        Args:
            key: The issue key.
            limit: The most comments to return; ``None`` returns every comment.
            expand: The extra blocks to include: ``attachments``, ``html`` or ``all``.

        Returns:
            The issue's comments.

        Examples:
            >>> [comment.text for comment in tracker.comments.list("DE-11", limit=500).root]
            ['first', 'second', 'third']
        """
        page_size = min(endpoints.PAGE_SIZE, limit) if limit else endpoints.PAGE_SIZE
        paged = endpoints.list_comments(key, page_size=page_size, expand=expand)
        return ItemList[Comment](list(self._session.iterate(paged, limit=limit)))

    def get(self, key: str, comment_id: int | str, *, expand: str | None = None) -> Comment:
        """``GET /issues/{key}/comments/{comment_id}`` — one comment. Returns it.

        ``comment_id`` is the numeric ``id`` or the string ``longId``. ``expand`` adds
        ``attachments``, ``html`` or ``all`` extra fields.

        Args:
            key: The issue key.
            comment_id: The comment's numeric ``id`` or string ``longId``.
            expand: The extra fields to include (``attachments``, ``html`` or ``all``).

        Returns:
            The comment.

        Examples:
            >>> tracker.comments.get("DE-5", 9001, expand="attachments,html").text_html
            '<p>My <strong>first</strong> comment</p>'
        """
        return self._session.send(endpoints.get_comment(key, comment_id, expand=expand))

    def add(self, key: str, body: CommentCreate) -> Comment:
        """``POST /issues/{key}/comments/`` — add a comment. Returns it.

        Args:
            key: The issue key.
            body: The new comment: its text and optional summonees and attachment ids.

        Returns:
            The created comment.

        Examples:
            >>> from ycli.yandex.tracker.models import CommentCreate
            >>> tracker.comments.add(
            ...     "DE-14", CommentCreate.model_validate({"text": "Готово ✅"})
            ... ).id
            141
        """
        return self._session.send(endpoints.add_comment(key, body))

    def edit(self, key: str, comment_id: int | str, body: CommentUpdate) -> Comment:
        """``PATCH /issues/{key}/comments/{comment_id}`` — edit a comment. Returns it.

        Args:
            key: The issue key.
            comment_id: The comment's numeric ``id`` or string ``longId``.
            body: The comment fields to change.

        Returns:
            The updated comment.

        Examples:
            >>> from ycli.yandex.tracker.comments.models import CommentUpdate
            >>> tracker.comments.edit(
            ...     "DE-16", "161", CommentUpdate.model_validate({"text": "fixed typo"})
            ... ).text
            'fixed typo'
        """
        return self._session.send(endpoints.edit_comment(key, comment_id, body))

    def delete(self, key: str, comment_id: str) -> None:
        """Delete a comment (``DELETE …/comments/{id}`` → 204). Raises on non-2xx.

        Args:
            key: The issue key.
            comment_id: The comment's id.

        Examples:
            >>> tracker.comments.delete("DE-17", "171")
        """
        self._session.send(endpoints.delete_comment(key, comment_id))

    def react(self, key: str, comment_id: int | str, name: str) -> Comment:
        """``POST …/comments/{comment_id}/reactions/{name}`` — add a reaction. Returns the comment.

        ``name`` is an uppercase reaction key (LIKE, DISLIKE, HEART, ROCKET, FIRE, …).

        Args:
            key: The issue key.
            comment_id: The comment's numeric ``id`` or string ``longId``.
            name: The reaction key.

        Returns:
            The comment the reaction was added to.

        Examples:
            >>> tracker.comments.react("DE-18", "181", "HEART").id
            181
        """
        return self._session.send(endpoints.react_to_comment(key, comment_id, name))
