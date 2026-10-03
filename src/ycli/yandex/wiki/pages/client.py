"""Wiki ``/pages`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.pages import endpoints
from ycli.yandex.wiki.pages.models import GridRefList, PageRefList, PageRevisionList

if TYPE_CHECKING:
    from ycli.yandex.wiki.models import AsyncOperation
    from ycli.yandex.wiki.pages.models import PageDeleteResult, PageDetails


class PagesClient(Resource):
    """``/pages``: get, descendants, grids, create, update, delete, append, clone, move.

    ``move``, ``revisions`` and ``backlinks`` call operations Yandex does not document (they are
    in the live OpenAPI only), so their contract may change without notice.
    """

    def get_by_id(self, page_id: int, fields: str | None = None) -> PageDetails:
        """``GET /pages/{id}?fields=`` → a single page by numeric id (raises on non-2xx).

        The slug-addressed sibling is :meth:`get`; use this when you hold the numeric id
        (e.g. from a descendants listing). ``fields`` is the same comma-separated selector
        (``content``, ``attributes``, ``breadcrumbs``, …); omit it for id/slug/title only.

        Args:
            page_id: The page's numeric id.
            fields: The comma-separated blocks to include.

        Returns:
            The page.

        Examples:
            >>> wiki.pages.get_by_id(4101, fields="content,breadcrumbs").content
            '# Arch'
        """
        return self._session.send(endpoints.get_page_by_id(page_id, fields=fields))

    def get(self, slug: str, fields: str | None = None) -> PageDetails:
        """``GET /pages?slug=&fields=`` → a single page (raises on non-2xx).

        Args:
            slug: The page's slug.
            fields: The comma-separated blocks to include.

        Returns:
            The page.

        Examples:
            >>> wiki.pages.get("team/handbook", fields="content,attributes").content
            '# Handbook'
        """
        return self._session.send(endpoints.get_page(slug, fields=fields))

    def descendants(
        self,
        slug: str,
        *,
        limit: int | None = None,
        actuality: str | None = None,
    ) -> PageRefList:
        """All descendant refs under ``slug``, draining ``next_cursor`` internally.

        Capped at ``limit``.

        Args:
            slug: The ancestor page's slug.
            limit: The most refs to return; ``None`` returns every ref.
            actuality: The page state to list.

        Returns:
            The descendants' refs.

        Examples:
            >>> [ref.slug for ref in wiki.pages.descendants("eng", limit=40).root]
            ['eng/a', 'eng/b']
        """
        paged = endpoints.list_descendants(slug, actuality=actuality)
        return PageRefList(list(self._session.iterate(paged, limit=limit)))

    def descendants_by_id(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        actuality: str | None = None,
    ) -> PageRefList:
        """All descendant refs under numeric ``page_id``, draining ``next_cursor`` internally.

        The numeric-id twin of :meth:`descendants`; capped at ``limit`` (``None`` = every ref).

        Args:
            page_id: The ancestor page's numeric id.
            limit: The most refs to return; ``None`` returns every ref.
            actuality: The page state to list.

        Returns:
            The descendants' refs.

        Examples:
            >>> [ref.slug for ref in wiki.pages.descendants_by_id(4210, limit=35).root]
            ['sales/a', 'sales/b']
        """
        paged = endpoints.list_descendants_by_id(page_id, actuality=actuality)
        return PageRefList(list(self._session.iterate(paged, limit=limit)))

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

        Args:
            page_id: The page's id.
            limit: The most grids to return; ``None`` returns every grid.
            order_by: The sort field: ``title`` or ``created_at``.

        Returns:
            The page's grids.

        Examples:
            >>> [grid.title for grid in wiki.pages.grids(4301, limit=30).root]
            ['Roadmap', 'Budget']
        """
        paged = endpoints.list_grids(page_id, order_by=order_by)
        return GridRefList(list(self._session.iterate(paged, limit=limit)))

    def create(self, body: dict[str, Any]) -> PageDetails:
        """``POST /pages`` — create. ``body`` carries ``content``/``title``/``slug``.

        Args:
            body: The new page: ``content``, ``title`` and ``slug``.

        Returns:
            The created page.

        Examples:
            >>> body = {"slug": "eng/new", "title": "New page", "content": "# New"}
            >>> wiki.pages.create(body).id
            4401
        """
        return self._session.send(endpoints.create_page(body))

    def update(self, page_id: int, body: dict[str, Any]) -> PageDetails:
        """``POST /pages/{id}`` — update (POST not PATCH; PATCH returns 405).

        Args:
            page_id: The page's id.
            body: The fields to change.

        Returns:
            The updated page.

        Examples:
            >>> wiki.pages.update(4403, {"content": "# Body only"}).id
            4403
        """
        return self._session.send(endpoints.update_page(page_id, body))

    def delete(self, page_id: int) -> PageDeleteResult:
        """``DELETE /pages/{id}`` → ``{recovery_token}``; keep the token to restore (undo).

        The returned :class:`PageDeleteResult` carries the ``recovery_token`` — the only handle
        to undo this delete, via ``RecoveryClient.restore`` (POST /recovery_tokens/{token}/recover).

        Args:
            page_id: The page's id.

        Returns:
            The result, carrying the deleted page's ``recovery_token``.

        Examples:
            >>> wiki.pages.delete(4501).recovery_token
            'recovery-token-2'
        """
        return self._session.send(endpoints.delete_page(page_id))

    def append_content(self, page_id: int, body: dict[str, Any]) -> PageDetails:
        """``POST /pages/{id}/append-content`` — append YFM without rewriting the whole body.

        ``body`` is a dumped :class:`PageAppendContent` (``{content, body?, section?, anchor?}``).
        Unlike :meth:`update` (which replaces the body), this adds to it; ``body.location`` /
        ``section`` / ``anchor`` pinpoint where. Returns the updated :class:`PageDetails`.

        Args:
            page_id: The page's id.
            body: The YFM to append and where to put it.

        Returns:
            The updated page.

        Examples:
            >>> body = {"content": "## Footer", "body": {"location": "bottom"}}
            >>> wiki.pages.append_content(4602, body).slug
            'eng/footer'
        """
        return self._session.send(endpoints.append_content(page_id, body))

    def clone(self, page_id: int, body: dict[str, Any]) -> AsyncOperation:
        """``POST /pages/{id}/clone`` — copy the page to a new address (async trigger).

        Returns a :class:`AsyncOperation`; poll its ``operation.id`` via
        ``OperationsClient.clone_get`` until terminal. ``body`` is a dumped :class:`PageClone`
        (``{target, title?, subscribe_me}``).

        Args:
            page_id: The page's id.
            body: The target address, an optional title and whether to subscribe the caller.

        Returns:
            The clone operation to poll.

        Examples:
            >>> body = {"target": "eng/copy", "title": "Copy", "subscribe_me": True}
            >>> wiki.pages.clone(4701, body).operation.id
            'task-4701'
        """
        return self._session.send(endpoints.clone_page(page_id, body))

    def move(self, body: dict[str, Any], *, dry_run: bool = False) -> AsyncOperation:
        """``POST /pages/move`` — give pages new addresses (async; undocumented, may change).

        The only way to rename or relocate a page: a page update has no ``slug``. Returns a
        :class:`AsyncOperation`; poll its ``operation.id`` via ``OperationsClient.move_get``
        until terminal. ``body`` is a dumped :class:`PageMove`
        (``{operations: [{source, target, next_to_slug?, position?}], copy_inherited_access}``;
        the API answers 400 unless ``copy_inherited_access`` is a boolean). A page moves with its
        subtree. ``dry_run=True`` validates the request without applying it, and the task id it
        returns answers 404 when polled.

        Args:
            body: The moves and ``copy_inherited_access``.
            dry_run: Validate the request without applying it.

        Returns:
            The move operation to poll.

        Examples:
            >>> body = {
            ...     "operations": [{"source": "eng/b", "target": "eng/c"}],
            ...     "copy_inherited_access": False,
            ... }
            >>> wiki.pages.move(body, dry_run=True).operation.id
            'mv-6101'
        """
        return self._session.send(endpoints.move_pages(body, dry_run=dry_run))

    def revisions(
        self,
        page_id: int,
        *,
        ids: str | None = None,
        limit: int | None = None,
    ) -> PageRevisionList:
        """``GET /pages/{id}/revisions`` → flat :class:`PageRevisionList`, draining ``next_cursor``.

        Undocumented by Yandex (live OpenAPI only), may change. A revision ``id`` is what
        ``GET /pages`` takes as ``revision_id``. ``ids`` keeps only these revisions (comma
        separated); capped at ``limit`` (``None`` = every revision).

        Args:
            page_id: The page's id.
            ids: The comma-separated revision ids to keep.
            limit: The most revisions to return; ``None`` returns every revision.

        Returns:
            The page's revisions.

        Examples:
            >>> revisions = wiki.pages.revisions(6201, ids="7002,7003", limit=40)
            >>> [revision.id for revision in revisions.root]
            [7003, 7002]
        """
        paged = endpoints.list_revisions(page_id, ids=ids)
        return PageRevisionList(list(self._session.iterate(paged, limit=limit)))

    def backlinks(
        self,
        page_id: int,
        *,
        for_cluster: bool = False,
        show_all: bool = False,
        limit: int | None = None,
    ) -> PageRefList:
        """``GET /pages/{id}/backlinks`` → refs of the pages that link here, draining the cursor.

        Undocumented by Yandex (live OpenAPI only), may change. ``for_cluster`` also reports links
        to the page's descendants. ``show_all`` is the API's flag of that name (no effect showed in
        a live check). The index lags a few seconds behind an edit. Capped at ``limit``
        (``None`` = every ref).

        Args:
            page_id: The page's id.
            for_cluster: Also report links to the page's descendants.
            show_all: The API's flag of that name.
            limit: The most refs to return; ``None`` returns every ref.

        Returns:
            The refs of the pages that link here.

        Examples:
            >>> refs = wiki.pages.backlinks(6301, for_cluster=True, show_all=True, limit=30)
            >>> [ref.slug for ref in refs.root]
            ['eng/linker-a', 'eng/linker-b']
        """
        paged = endpoints.list_backlinks(page_id, for_cluster=for_cluster, show_all=show_all)
        return PageRefList(list(self._session.iterate(paged, limit=limit)))
