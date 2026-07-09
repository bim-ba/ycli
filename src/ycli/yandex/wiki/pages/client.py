"""Declarative Yandex Wiki /pages client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import uplink

from ycli.yandex.pagination import CursorStrategy
from ycli.yandex.wiki.base import WikiResource
from ycli.yandex.wiki.pages.models import (
    DescendantsResponse,
    GridRefList,
    GridsResponse,
    PageDeleteResult,
    PageDetails,
    PageRefList,
)


class PagesClient(WikiResource):
    """Declarative HTTP for ``/pages`` (get, descendants, grids, create, update, delete, append)."""

    @uplink.returns.json()
    @uplink.get("pages/{page_id}")
    def get_by_id(
        self,
        page_id: uplink.Path,
        fields: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> PageDetails:  # ty: ignore[empty-body]
        """``GET /pages/{id}?fields=`` → a single page by numeric id (raises on non-2xx).

        The slug-addressed sibling is :meth:`get`; use this when you hold the numeric id
        (e.g. from a descendants listing). ``fields`` is the same comma-separated selector
        (``content``, ``attributes``, ``breadcrumbs``, …); omit it for id/slug/title only.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.get_by_id(12345, fields="content").title  # doctest: +SKIP
            'Архитектура данных'
        """

    @uplink.returns.json()
    @uplink.get("pages")
    def get(
        self,
        slug: uplink.Query,
        fields: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> PageDetails:  # ty: ignore[empty-body]
        """``GET /pages?slug=&fields=`` → a single page (raises on non-2xx).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.get(slug="data/architecture", fields="content").title  # doctest: +SKIP
            'Архитектура данных'
        """

    @uplink.returns.json()
    @uplink.get("pages/descendants")
    def _descendants_page(
        self,
        slug: uplink.Query,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
        cursor: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        actuality: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> DescendantsResponse:  # ty: ignore[empty-body]
        """One raw page of ``{id, slug}`` refs + ``next_cursor``.

        Internal; callers use ``descendants``."""

    def descendants(
        self,
        slug: str,
        *,
        limit: int | None = None,
        actuality: str | None = None,
    ) -> PageRefList:
        """All descendant refs under ``slug``, draining ``next_cursor`` internally.

        Capped at ``limit``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> refs = client.pages.descendants(slug="data", limit=50)  # doctest: +SKIP
            >>> refs.root[0].slug  # doctest: +SKIP
            'data/architecture'
        """
        strategy = CursorStrategy(
            extract=lambda page: page.results,
            next_of=lambda page: page.next_cursor,
        )
        refs = strategy.collect(
            lambda cursor: self._descendants_page(
                slug=slug, page_size=100, cursor=cursor, actuality=actuality
            ),
            limit,
        )
        return PageRefList(refs)

    @uplink.returns.json()
    @uplink.get("pages/{page_id}/descendants")
    def _descendants_by_id_page(
        self,
        page_id: uplink.Path,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
        cursor: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        actuality: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> DescendantsResponse:  # ty: ignore[empty-body]
        """One raw page of ``{id, slug}`` refs + ``next_cursor`` (by numeric id).

        Internal; callers use ``descendants_by_id``."""

    def descendants_by_id(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        actuality: str | None = None,
    ) -> PageRefList:
        """All descendant refs under numeric ``page_id``, draining ``next_cursor`` internally.

        The numeric-id twin of :meth:`descendants`; capped at ``limit`` (``None`` = every ref).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> refs = client.pages.descendants_by_id(12345, limit=50)  # doctest: +SKIP
            >>> refs.root[0].slug  # doctest: +SKIP
            'data/architecture'
        """
        strategy = CursorStrategy(
            extract=lambda page: page.results,
            next_of=lambda page: page.next_cursor,
        )
        refs = strategy.collect(
            lambda cursor: self._descendants_by_id_page(
                page_id, page_size=100, cursor=cursor, actuality=actuality
            ),
            limit,
        )
        return PageRefList(refs)

    @uplink.returns.json()
    @uplink.get("pages/{page_id}/grids")
    def _grids_page(
        self,
        page_id: uplink.Path,
        page_size: uplink.Query = 50,  # ty: ignore[invalid-parameter-default]
        cursor: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        order_by: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> GridsResponse:  # ty: ignore[empty-body]
        """One raw page of grid refs + ``next_cursor`` (internal; callers use ``grids``)."""

    def grids(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> GridRefList:
        """``GET /pages/{id}/grids`` → flat :class:`GridRefList`, draining ``next_cursor``.

        Dynamic tables (grids) attached to the page. Capped at ``limit`` (``None`` = every
        grid); ``order_by`` sorts the server-side listing (``title`` or ``created_at``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.grids(12345, limit=50).root[0].title  # doctest: +SKIP
            'Roadmap'
        """
        strategy = CursorStrategy(
            extract=lambda page: page.results,
            next_of=lambda page: page.next_cursor,
        )
        grids = strategy.collect(
            lambda cursor: self._grids_page(
                page_id, page_size=50, cursor=cursor, order_by=order_by
            ),
            limit,
        )
        return GridRefList(grids)

    @uplink.returns.json()
    @uplink.json
    @uplink.post("pages")
    def create(self, body: uplink.Body) -> PageDetails:  # ty: ignore[empty-body]
        """``POST /pages`` — create. ``body`` carries ``content``/``title``/``slug``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.create(
            ...     {"slug": "data/guides/x", "title": "X", "content": "# X"}
            ... ).id  # doctest: +SKIP
            12345
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("pages/{page_id}")
    def update(self, page_id: uplink.Path, body: uplink.Body) -> PageDetails:  # ty: ignore[empty-body]
        """``POST /pages/{id}`` — update (POST not PATCH; PATCH returns 405).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.update(12345, {"content": "# Updated"}).id  # doctest: +SKIP
            12345
        """

    @uplink.returns.json()
    @uplink.delete("pages/{page_id}")
    def delete(self, page_id: uplink.Path) -> PageDeleteResult:  # ty: ignore[empty-body]
        """``DELETE /pages/{id}`` → ``{recovery_token}``; keep the token to restore (undo).

        The returned :class:`PageDeleteResult` carries the ``recovery_token`` — the only handle
        to undo this delete, via ``RecoveryClient.restore`` (POST /recovery_tokens/{token}/recover).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.delete(12345).recovery_token  # doctest: +SKIP
            'a1b2c3d4-…'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("pages/{page_id}/append-content")
    def append_content(self, page_id: uplink.Path, body: uplink.Body) -> PageDetails:  # ty: ignore[empty-body]
        """``POST /pages/{id}/append-content`` — append YFM without rewriting the whole body.

        ``body`` is a dumped :class:`PageAppendContent` (``{content, body?, section?, anchor?}``).
        Unlike :meth:`update` (which replaces the body), this adds to it; ``body.location`` /
        ``section`` / ``anchor`` pinpoint where. Returns the updated :class:`PageDetails`.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.append_content(
            ...     12345, {"content": "## More", "body": {"location": "bottom"}}
            ... ).id  # doctest: +SKIP
            12345
        """
