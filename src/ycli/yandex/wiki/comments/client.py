"""Declarative Yandex Wiki /pages/{id}/comments client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

from collections import defaultdict
from collections.abc import Sequence

import uplink

from ycli.yandex.pagination import CursorStrategy
from ycli.yandex.wiki.base import WikiResource
from ycli.yandex.wiki.comments.models import (
    Comment,
    CommentCreated,
    CommentDeleteResult,
    CommentList,
    CommentsResponse,
)


class CommentsClient(WikiResource):
    """HTTP for ``/pages/{id}/comments`` (list, create, delete); ``thread`` rebuilds client-side."""

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

    def thread(self, page_id: int, comment_id: int, *, limit: int | None = None) -> CommentList:
        """The comment ``comment_id`` followed by its replies, reconstructed from ``comments list``.

        The Wiki ``/comments/{id}/thread`` endpoint returns ``{"results": []}`` for real
        parent/child pairs, and the flat listing returns a reply as a *sibling* of its parent
        (tagged only by ``parent_id``; ``thread_id`` / ``thread_info`` are ``null``). So this
        fetches every comment on the page and rebuilds the thread client-side by chaining
        ``parent_id`` from the target to any depth. Returns a flat :class:`CommentList` — the
        target comment first, then its descendants in depth-first order (each carrying the
        ``parent_id`` that wires it to its parent) — or an empty list if ``comment_id`` is not
        found. ``limit`` caps the number of replies collected (``None`` = every reply).

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

    @uplink.returns.json()
    @uplink.json
    @uplink.post("pages/{page_id}/comments")
    def create(self, page_id: uplink.Path, body: uplink.Body) -> CommentCreated:  # ty: ignore[empty-body]
        """``POST /pages/{id}/comments`` — add a comment; returns a :class:`CommentCreated`.

        ``body`` is a dumped :class:`CommentCreate` (``body`` + optional
        ``inline_text`` / ``parent_id`` / ``thread_id``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.create(12345, {"body": "LGTM"}).id  # doctest: +SKIP
            678
        """

    @uplink.returns.json()
    @uplink.delete("pages/{page_id}/comments/{comment_id}")
    def delete(self, page_id: uplink.Path, comment_id: uplink.Path) -> CommentDeleteResult:  # ty: ignore[empty-body]
        """``DELETE /pages/{id}/comments/{comment_id}`` → ``{comments_count}`` left on the page.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.comments.delete(12345, 678).comments_count  # doctest: +SKIP
            4
        """
