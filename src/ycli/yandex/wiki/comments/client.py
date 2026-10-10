"""Wiki ``/pages/{id}/comments`` client on the httpx2 core; ``thread_list`` rebuilds client-side."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.wiki.comments import endpoints
from ycli.yandex.wiki.comments.models import Comment, CommentCreate

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.core.listing import Listing
    from ycli.yandex.wiki.comments.models import CommentCreated, CommentDeleteResult


class CommentsClient(Resource):
    """``/pages/{id}/comments``: list, create, delete; ``thread_list`` rebuilds a thread."""

    def list(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        next: str | None = None,
        order_by: str | None = None,
        order_direction: str | None = None,
        status_filter: str | None = None,
    ) -> Listing[Comment]:
        """``GET /pages/{id}/comments`` → flat ``ItemList[Comment]``, draining ``next_cursor``.

        Capped at ``limit`` (``None`` = every comment).

        Args:
            page_id: The page's id.
            limit: The most comments to return; ``None`` returns every comment.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.
            order_by: The sort field; the API accepts ``created_at``.
            order_direction: The sort direction for ``order_by``: ``asc`` or ``desc``.
            status_filter: Keep only ``resolved`` or only ``unresolved`` comments.

        Returns:
            The page's comments.

        Examples:
            >>> [comment.author for comment in wiki.comments.list(5501, limit=45)]
            ['Vera', 'Ivan']
        """
        paged = endpoints.list_(
            page_id, order_by=order_by, order_direction=order_direction, status_filter=status_filter
        )
        return self._session.iterate(paged, limit=limit, next=next)

    def thread_list(
        self, page_id: int, comment_id: int, *, limit: int | None = None
    ) -> ItemList[Comment]:
        """The comment ``comment_id`` followed by its replies, reconstructed from ``comments list``.

        The Wiki ``/comments/{id}/thread`` endpoint (:meth:`thread_get`) returns
        ``{"results": []}`` for real parent/child pairs, and the flat listing returns a reply as a
        *sibling* of its parent (tagged only by ``parent_id``; ``thread_id`` / ``thread_info`` are
        ``null``). So this fetches every comment on the page and rebuilds the thread client-side
        by chaining ``parent_id`` from the target to any depth. Returns a flat
        ``ItemList[Comment]`` — the target comment first, then its descendants in depth-first order
        (each carrying the ``parent_id`` that wires it to its parent) — or an empty list if
        ``comment_id`` is not found. ``limit`` caps the replies collected (``None`` = every reply).

        Args:
            page_id: The page's id.
            comment_id: The id of the thread's first comment.
            limit: The most replies to collect; ``None`` collects every reply.

        Returns:
            The comment and its replies.

        Examples:
            >>> [
            ...     comment.content
            ...     for comment in wiki.comments.thread_list(5503, 5511, limit=15).root
            ... ]
            ['Ship it?', 'Agreed']
        """
        comments = list(self.list(page_id=page_id))
        return self._collect_thread(comments, comment_id, limit=limit)

    @staticmethod
    def _collect_thread(
        comments: Sequence[Comment],  # ``Sequence``, not ``list``: the ``list`` method shadows it
        comment_id: int,
        *,
        limit: int | None = None,
    ) -> ItemList[Comment]:
        """Reconstruct one thread from a flat comment list (pure shaping — no HTTP).

        Groups comments by ``parent_id`` and walks the ``parent_id`` chain from ``comment_id`` to
        any depth, returning a ``ItemList[Comment]`` of the target comment followed by its
        descendants in depth-first order. ``limit`` bounds the number of descendants collected;
        returns an empty list if ``comment_id`` is absent. A ``seen`` set guards against
        self/cyclic ``parent_id`` references.

        Args:
            comments: The page's flat comment list.
            comment_id: The id of the thread's first comment.
            limit: The most descendants to collect; ``None`` collects every descendant.

        Returns:
            The comment followed by its descendants.
        """
        by_parent: dict[int, list[Comment]] = defaultdict(list)
        by_id: dict[int, Comment] = {}
        for comment in comments:
            if comment.id is not None:
                by_id[comment.id] = comment
            if comment.parent_id is not None:
                by_parent[comment.parent_id].append(comment)

        root = by_id.get(comment_id)
        if root is None:
            return ItemList[Comment]([])

        thread: list[Comment] = [root]
        seen: set[int] = {comment_id}

        def walk(node: Comment) -> None:
            for child in by_parent.get(node.id, []):
                if limit is not None and len(thread) - 1 >= limit:
                    return
                if child.id is not None and child.id in seen:
                    continue
                if child.id is not None:
                    seen.add(child.id)
                thread.append(child)
                walk(child)

        walk(root)
        return ItemList[Comment](thread)

    # violation(naming): the thread of one comment is one object, its comments are the list
    def thread_get(
        self, page_id: int, comment_id: int, *, limit: int | None = None, next: str | None = None
    ) -> Listing[Comment]:
        """``GET /pages/{id}/comments/{comment_id}/thread`` → what the server calls the thread.

        Checked live on 2026-10-02: the endpoint answers ``{"results": []}`` for a root comment
        and for its replies, plain or inline, so this returns an empty list for every real
        thread. Use :meth:`thread_list`, which rebuilds the thread from :meth:`list`; this raw call
        stays for the day the server fills it in. Capped at ``limit`` (``None`` = everything).

        Args:
            page_id: The page's id.
            comment_id: The comment's id.
            limit: The most comments to return; ``None`` returns everything.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.

        Returns:
            The thread's comments.

        Examples:
            >>> wiki.comments.thread_get(5508, 5512).collect().items
            []
        """
        paged = endpoints.thread_get(page_id, comment_id)
        return self._session.iterate(paged, limit=limit, next=next)

    def create(self, page_id: int, body: CommentCreate) -> CommentCreated:
        """``POST /pages/{id}/comments`` — add a comment; returns a :class:`CommentCreated`.

        ``body`` is a :class:`CommentCreate` (``body`` + optional
        ``inline_text`` / ``parent_id`` / ``thread_id``).

        Args:
            page_id: The page's id.
            body: The comment: ``body`` and optional ``inline_text``, ``parent_id``, ``thread_id``.

        Returns:
            The created comment.

        Examples:
            >>> from ycli.yandex.wiki.comments.models import CommentCreate
            >>> wiki.comments.create(5505, CommentCreate.model_validate({"body": "Plain note"})).id
            5515
        """
        return self._session.send(endpoints.create(page_id, body))

    def delete(self, page_id: int, comment_id: int) -> CommentDeleteResult:
        """``DELETE /pages/{id}/comments/{comment_id}`` → ``{comments_count}`` left on the page.

        Args:
            page_id: The page's id.
            comment_id: The comment's id.

        Returns:
            The result, whose ``comments_count`` is the number of comments left.

        Examples:
            >>> wiki.comments.delete(5506, 5516).comments_count
            4
        """
        return self._session.send(endpoints.delete(page_id, comment_id))
