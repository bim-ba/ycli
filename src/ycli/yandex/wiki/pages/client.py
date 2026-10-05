"""Wiki ``/pages`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.wiki.pages import endpoints
from ycli.yandex.wiki.pages.models import (
    GridRef,
    PageAppendContent,
    PageClone,
    PageCreate,
    PageMove,
    PageRef,
    PageRevision,
    PageUpdate,
)

if TYPE_CHECKING:
    from ycli.yandex.wiki.models import AsyncOperation
    from ycli.yandex.wiki.pages.models import (
        PageDeleteResult,
        PageDetails,
        SearchPage,
        SearchRequest,
    )


class PagesClient(Resource):
    """``/pages``: get, descendants, grids, create, update, delete, append, clone, move.

    ``move``, ``revisions_list`` and ``backlinks_list`` call operations Yandex does not document
    (they are in the live OpenAPI only), so their contract may change without notice.
    """

    def get_by_id(
        self,
        page_id: int,
        fields: str | None = None,
        *,
        revision_id: int | None = None,
        raise_on_redirect: bool | None = None,
    ) -> PageDetails:
        """``GET /pages/{id}?fields=`` → a single page by numeric id (raises on non-2xx).

        The slug-addressed sibling is :meth:`get`; use this when you hold the numeric id
        (e.g. from a descendants listing). ``fields`` is the same comma-separated selector
        (``content``, ``attributes``, ``breadcrumbs``, …); omit it for id/slug/title only.

        Args:
            page_id: The page's numeric id.
            fields: The comma-separated blocks to include.
            revision_id: The past revision to show, from :meth:`revisions_list`; ``None`` shows the
                current one.
            raise_on_redirect: Answer with an error when the page is a redirect, instead of
                the page it leads to.

        Returns:
            The page.

        Examples:
            >>> wiki.pages.get_by_id(4101, fields="content,breadcrumbs").content
            '# Arch'
        """
        endpoint = endpoints.get_by_id(
            page_id, fields=fields, revision_id=revision_id, raise_on_redirect=raise_on_redirect
        )
        return self._session.send(endpoint)

    def get(
        self,
        slug: str,
        fields: str | None = None,
        *,
        revision_id: int | None = None,
        raise_on_redirect: bool | None = None,
    ) -> PageDetails:
        """``GET /pages?slug=&fields=`` → a single page (raises on non-2xx).

        Args:
            slug: The page's slug.
            fields: The comma-separated blocks to include.
            revision_id: The past revision to show, from :meth:`revisions_list`; ``None`` shows the
                current one.
            raise_on_redirect: Answer with an error when the page is a redirect, instead of
                the page it leads to.

        Returns:
            The page.

        Examples:
            >>> wiki.pages.get("team/handbook", fields="content,attributes").content
            '# Handbook'
        """
        endpoint = endpoints.get(
            slug, fields=fields, revision_id=revision_id, raise_on_redirect=raise_on_redirect
        )
        return self._session.send(endpoint)

    def descendants_list(
        self,
        slug: str,
        *,
        limit: int | None = None,
        actuality: str | None = None,
        include_self: bool | None = None,
        show_all: bool | None = None,
    ) -> ItemList[PageRef]:
        """All descendant refs under ``slug``, draining ``next_cursor`` internally.

        Capped at ``limit``.

        Args:
            slug: The ancestor page's slug.
            limit: The most refs to return; ``None`` returns every ref.
            actuality: The page state to list.
            include_self: Also return the ancestor page itself.
            show_all: The API's flag of that name.

        Returns:
            The descendants' refs.

        Examples:
            >>> [ref.slug for ref in wiki.pages.descendants_list("eng", limit=40).root]
            ['eng/a', 'eng/b']
        """
        paged = endpoints.descendants_list(
            slug, actuality=actuality, include_self=include_self, show_all=show_all
        )
        return ItemList[PageRef](list(self._session.iterate(paged, limit=limit)))

    def descendants_list_by_id(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        actuality: str | None = None,
        include_self: bool | None = None,
        show_all: bool | None = None,
    ) -> ItemList[PageRef]:
        """All descendant refs under numeric ``page_id``, draining ``next_cursor`` internally.

        The numeric-id twin of :meth:`descendants_list`; capped at ``limit`` (``None`` = every ref).

        Args:
            page_id: The ancestor page's numeric id.
            limit: The most refs to return; ``None`` returns every ref.
            actuality: The page state to list.
            include_self: Also return the ancestor page itself.
            show_all: The API's flag of that name.

        Returns:
            The descendants' refs.

        Examples:
            >>> [ref.slug for ref in wiki.pages.descendants_list_by_id(4210, limit=35).root]
            ['sales/a', 'sales/b']
        """
        paged = endpoints.descendants_list_by_id(
            page_id, actuality=actuality, include_self=include_self, show_all=show_all
        )
        return ItemList[PageRef](list(self._session.iterate(paged, limit=limit)))

    def grids_list(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        order_by: str | None = None,
        order_direction: str | None = None,
    ) -> ItemList[GridRef]:
        """``GET /pages/{id}/grids`` → flat ``ItemList[GridRef]``, draining ``next_cursor``.

        Dynamic tables (grids) attached to the page. Capped at ``limit`` (``None`` = every
        grid); ``order_by`` sorts the server-side listing (``title`` or ``created_at``).

        Args:
            page_id: The page's id.
            limit: The most grids to return; ``None`` returns every grid.
            order_by: The sort field: ``title`` or ``created_at``.
            order_direction: The sort direction for ``order_by``: ``asc`` or ``desc``.

        Returns:
            The page's grids.

        Examples:
            >>> [grid.title for grid in wiki.pages.grids_list(4301, limit=30).root]
            ['Roadmap', 'Budget']
        """
        paged = endpoints.grids_list(page_id, order_by=order_by, order_direction=order_direction)
        return ItemList[GridRef](list(self._session.iterate(paged, limit=limit)))

    def create(
        self, body: PageCreate, *, fields: str | None = None, is_silent: bool | None = None
    ) -> PageDetails:
        """``POST /pages`` — create. ``body`` carries ``content``/``title``/``slug``.

        Args:
            body: The new page: ``content``, ``title`` and ``slug``.
            fields: The comma-separated blocks to include in the reply.
            is_silent: Do not notify the page's subscribers.

        Returns:
            The created page.

        Examples:
            >>> from ycli.yandex.wiki.pages.models import PageCreate
            >>> body = PageCreate.model_validate(
            ...     {"slug": "eng/new", "title": "New page", "content": "# New"}
            ... )
            >>> wiki.pages.create(body).id
            4401
        """
        return self._session.send(endpoints.create(body, fields=fields, is_silent=is_silent))

    def update(
        self,
        page_id: int,
        body: PageUpdate,
        *,
        fields: str | None = None,
        is_silent: bool | None = None,
        allow_merge: bool | None = None,
    ) -> PageDetails:
        """``POST /pages/{id}`` — update (POST not PATCH; PATCH returns 405).

        Args:
            page_id: The page's id.
            body: The fields to change.
            fields: The comma-separated blocks to include in the reply.
            is_silent: Do not notify the page's subscribers.
            allow_merge: Merge with a concurrent edit (3-way merge) instead of failing on the
                conflict.

        Returns:
            The updated page.

        Examples:
            >>> from ycli.yandex.wiki.pages.models import PageUpdate
            >>> wiki.pages.update(4403, PageUpdate.model_validate({"content": "# Body only"})).id
            4403
        """
        endpoint = endpoints.update(
            page_id, body, fields=fields, is_silent=is_silent, allow_merge=allow_merge
        )
        return self._session.send(endpoint)

    def delete(self, page_id: int, *, recursive: bool | None = None) -> PageDeleteResult:
        """``DELETE /pages/{id}`` → ``{recovery_token}``; keep the token to restore (undo).

        The returned :class:`PageDeleteResult` carries the ``recovery_token`` — the only handle
        to undo this delete, via ``RecoveryClient.restore`` (POST /recovery_tokens/{token}/recover).

        Args:
            page_id: The page's id.
            recursive: Also delete every page under it.

        Returns:
            The result, carrying the deleted page's ``recovery_token``.

        Examples:
            >>> wiki.pages.delete(4501).recovery_token
            'recovery-token-2'
        """
        return self._session.send(endpoints.delete(page_id, recursive=recursive))

    def append(
        self,
        page_id: int,
        body: PageAppendContent,
        *,
        fields: str | None = None,
        is_silent: bool | None = None,
    ) -> PageDetails:
        """``POST /pages/{id}/append-content`` — append YFM without rewriting the whole body.

        ``body`` is a :class:`PageAppendContent` (``{content, body?, section?, anchor?}``).
        Unlike :meth:`update` (which replaces the body), this adds to it; ``body.location`` /
        ``section`` / ``anchor`` pinpoint where. Returns the updated :class:`PageDetails`.

        Args:
            page_id: The page's id.
            body: The YFM to append and where to put it.
            fields: The comma-separated blocks to include in the reply.
            is_silent: Do not notify the page's subscribers.

        Returns:
            The updated page.

        Examples:
            >>> from ycli.yandex.wiki.pages.models import PageAppendContent
            >>> body = PageAppendContent.model_validate(
            ...     {"content": "## Footer", "body": {"location": "bottom"}}
            ... )
            >>> wiki.pages.append(4602, body).slug
            'eng/footer'
        """
        endpoint = endpoints.append(page_id, body, fields=fields, is_silent=is_silent)
        return self._session.send(endpoint)

    def clone(self, page_id: int, body: PageClone) -> AsyncOperation:
        """``POST /pages/{id}/clone`` — copy the page to a new address (async trigger).

        Returns a :class:`AsyncOperation`; poll its ``operation.id`` via
        ``OperationsClient.clone_get`` until terminal. ``body`` is a :class:`PageClone`
        (``{target, title?, subscribe_me}``).

        Args:
            page_id: The page's id.
            body: The target address, an optional title and whether to subscribe the caller.

        Returns:
            The clone operation to poll.

        Examples:
            >>> from ycli.yandex.wiki.pages.models import PageClone
            >>> body = PageClone.model_validate(
            ...     {"target": "eng/copy", "title": "Copy", "subscribe_me": True}
            ... )
            >>> wiki.pages.clone(4701, body).operation.id
            'task-4701'
        """
        return self._session.send(endpoints.clone(page_id, body))

    def move(self, body: PageMove, *, validate_only: bool | None = None) -> AsyncOperation:
        """``POST /pages/move`` — give pages new addresses (async; undocumented, may change).

        The only way to rename or relocate a page: a page update has no ``slug``. Returns a
        :class:`AsyncOperation`; poll its ``operation.id`` via ``OperationsClient.move_get``
        until terminal. ``body`` is a :class:`PageMove`
        (``{operations: [{source, target, next_to_slug?, position?}], copy_inherited_access}``;
        the API answers 400 unless ``copy_inherited_access`` is a boolean). A page moves with its
        subtree. ``validate_only=True`` validates the request without applying it, and the task id
        it returns answers 404 when polled.

        Args:
            body: The moves and ``copy_inherited_access``.
            validate_only: Validate the request without applying it.

        Returns:
            The move operation to poll.

        Examples:
            >>> from ycli.yandex.wiki.pages.models import PageMove
            >>> body = PageMove.model_validate(
            ...     {
            ...         "operations": [{"source": "eng/b", "target": "eng/c"}],
            ...         "copy_inherited_access": False,
            ...     }
            ... )
            >>> wiki.pages.move(body, validate_only=True).operation.id
            'mv-6101'
        """
        return self._session.send(endpoints.move(body, validate_only=validate_only))

    def revisions_list(
        self,
        page_id: int,
        *,
        ids: str | None = None,
        limit: int | None = None,
    ) -> ItemList[PageRevision]:
        """``GET /pages/{id}/revisions`` → ``ItemList[PageRevision]``, draining ``next_cursor``.

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
            >>> revisions = wiki.pages.revisions_list(6201, ids="7002,7003", limit=40)
            >>> [revision.id for revision in revisions.root]
            [7003, 7002]
        """
        paged = endpoints.revisions_list(page_id, ids=ids)
        return ItemList[PageRevision](list(self._session.iterate(paged, limit=limit)))

    def backlinks_list(
        self,
        page_id: int,
        *,
        for_cluster: bool | None = None,
        show_all: bool | None = None,
        limit: int | None = None,
    ) -> ItemList[PageRef]:
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
            >>> refs = wiki.pages.backlinks_list(6301, for_cluster=True, show_all=True, limit=30)
            >>> [ref.slug for ref in refs.root]
            ['eng/linker-a', 'eng/linker-b']
        """
        paged = endpoints.backlinks_list(page_id, for_cluster=for_cluster, show_all=show_all)
        return ItemList[PageRef](list(self._session.iterate(paged, limit=limit)))

    def search(self, body: SearchRequest) -> SearchPage:
        """``POST /search`` → one :class:`SearchPage` of hits for the query.

        ``body`` is a :class:`SearchRequest` (``query``, optional ``filters``, ``cursor``,
        ``limit``, ``order_by``, ``highlight``). Pages are walked by hand: ``next_cursor`` is the
        next page's number as text, but the API also sets it after an empty page and repeats
        hits for a page past the last one, so there is no reliable end to drain to. Stop at the
        first page with no results or when ``next_cursor`` is ``None``.

        Args:
            body: The search request: ``query`` and optional ``filters``, ``cursor``, ``limit``,
                ``order_by``, ``highlight``.

        Returns:
            The page of hits.

        Examples:
            >>> from ycli.yandex.wiki.pages.models import SearchRequest
            >>> body = SearchRequest(query="quarterly roadmap", cursor=3, limit=25)
            >>> page = wiki.pages.search(body)
            >>> page.results[0].slug, page.next_cursor
            ('team/roadmap', '4')
        """
        return self._session.send(endpoints.search(body))
