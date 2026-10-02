"""Wiki ``/pages/{id}/comments`` client on the httpx2 core; ``thread`` rebuilds client-side."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.comments import endpoints
from ycli.yandex.wiki.comments.models import CommentList

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.wiki.comments.models import Comment, CommentCreated, CommentDeleteResult


class CommentsClient(Resource):
    """``/pages/{id}/comments``: list, create, delete; ``thread`` rebuilds a thread client-side."""

    def list(self, page_id: int, *, limit: int | None = None) -> CommentList:
        """``GET /pages/{id}/comments`` → flat :class:`CommentList`, draining ``next_cursor``.

        Capped at ``limit`` (``None`` = every comment).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.list(12345, limit=50).root[0].author  # doctest: +SKIP
            'Сава Знатнов'
        """
        paged = endpoints.list_comments(page_id)
        return CommentList(list(self._session.iterate(paged, limit=limit)))

    def thread(self, page_id: int, comment_id: int, *, limit: int | None = None) -> CommentList:
        """The comment ``comment_id`` followed by its replies, reconstructed from ``comments list``.

        The Wiki ``/comments/{id}/thread`` endpoint (:meth:`thread_get`) returns
        ``{"results": []}`` for real parent/child pairs, and the flat listing returns a reply as a
        *sibling* of its parent (tagged only by ``parent_id``; ``thread_id`` / ``thread_info`` are
        ``null``). So this fetches every comment on the page and rebuilds the thread client-side
        by chaining ``parent_id`` from the target to any depth. Returns a flat
        :class:`CommentList` — the target comment first, then its descendants in depth-first order
        (each carrying the ``parent_id`` that wires it to its parent) — or an empty list if
        ``comment_id`` is not found. ``limit`` caps the replies collected (``None`` = every reply).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.thread(12345, 678).root[1].content  # doctest: +SKIP
            'Согласен'
        """
        comments = self.list(page_id=page_id).root
        return self._collect_thread(comments, comment_id, limit=limit)

    @staticmethod
    def _collect_thread(
        comments: Sequence[Comment],  # ``Sequence``, not ``list``: the ``list`` method shadows it
        comment_id: int,
        *,
        limit: int | None = None,
    ) -> CommentList:
        """Reconstruct one thread from a flat comment list (pure shaping — no HTTP).

        Groups comments by ``parent_id`` and walks the ``parent_id`` chain from ``comment_id`` to
        any depth, returning a :class:`CommentList` of the target comment followed by its
        descendants in depth-first order. ``limit`` bounds the number of descendants collected;
        returns an empty list if ``comment_id`` is absent. A ``seen`` set guards against
        self/cyclic ``parent_id`` references.
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
            return CommentList([])

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
        return CommentList(thread)

    def thread_get(self, page_id: int, comment_id: int, *, limit: int | None = None) -> CommentList:
        """``GET /pages/{id}/comments/{comment_id}/thread`` → what the server calls the thread.

        Checked live on 2026-10-02: the endpoint answers ``{"results": []}`` for a root comment
        and for its replies, plain or inline, so this returns an empty list for every real
        thread. Use :meth:`thread`, which rebuilds the thread from :meth:`list`; this raw call
        stays for the day the server fills it in. Capped at ``limit`` (``None`` = everything).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.thread_get(12345, 678).root  # doctest: +SKIP
            []
        """
        paged = endpoints.get_thread(page_id, comment_id)
        return CommentList(list(self._session.iterate(paged, limit=limit)))

    def create(self, page_id: int, body: dict[str, Any]) -> CommentCreated:
        """``POST /pages/{id}/comments`` — add a comment; returns a :class:`CommentCreated`.

        ``body`` is a dumped :class:`CommentCreate` (``body`` + optional
        ``inline_text`` / ``parent_id`` / ``thread_id``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.create(12345, {"body": "LGTM"}).id  # doctest: +SKIP
            678
        """
        return self._session.send(endpoints.create_comment(page_id, body))

    def delete(self, page_id: int, comment_id: int) -> CommentDeleteResult:
        """``DELETE /pages/{id}/comments/{comment_id}`` → ``{comments_count}`` left on the page.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.delete(12345, 678).comments_count  # doctest: +SKIP
            4
        """
        return self._session.send(endpoints.delete_comment(page_id, comment_id))
