"""Wiki ``/pages`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.pages import endpoints
from ycli.yandex.wiki.pages.models import GridRefList, PageRefList

if TYPE_CHECKING:
    from ycli.yandex.wiki.pages.models import PageCloneOperation, PageDeleteResult, PageDetails


class PagesClient(Resource):
    """``/pages``: get, descendants, grids, create, update, delete, append, clone."""

    def get_by_id(self, page_id: int, fields: str | None = None) -> PageDetails:
        """``GET /pages/{id}?fields=`` → a single page by numeric id (raises on non-2xx).

        The slug-addressed sibling is :meth:`get`; use this when you hold the numeric id
        (e.g. from a descendants listing). ``fields`` is the same comma-separated selector
        (``content``, ``attributes``, ``breadcrumbs``, …); omit it for id/slug/title only.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.get_by_id(12345, fields="content").title  # doctest: +SKIP
            'Архитектура данных'
        """
        return self._session.send(endpoints.get_page_by_id(page_id, fields=fields))

    def get(self, slug: str, fields: str | None = None) -> PageDetails:
        """``GET /pages?slug=&fields=`` → a single page (raises on non-2xx).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.get(slug="data/architecture", fields="content").title  # doctest: +SKIP
            'Архитектура данных'
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

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> refs = client.pages.descendants(slug="data", limit=50)  # doctest: +SKIP
            >>> refs.root[0].slug  # doctest: +SKIP
            'data/architecture'
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

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> refs = client.pages.descendants_by_id(12345, limit=50)  # doctest: +SKIP
            >>> refs.root[0].slug  # doctest: +SKIP
            'data/architecture'
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

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.grids(12345, limit=50).root[0].title  # doctest: +SKIP
            'Roadmap'
        """
        paged = endpoints.list_grids(page_id, order_by=order_by)
        return GridRefList(list(self._session.iterate(paged, limit=limit)))

    def create(self, body: dict[str, Any]) -> PageDetails:
        """``POST /pages`` — create. ``body`` carries ``content``/``title``/``slug``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.create(
            ...     {"slug": "data/guides/x", "title": "X", "content": "# X"}
            ... ).id  # doctest: +SKIP
            12345
        """
        return self._session.send(endpoints.create_page(body))

    def update(self, page_id: int, body: dict[str, Any]) -> PageDetails:
        """``POST /pages/{id}`` — update (POST not PATCH; PATCH returns 405).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.update(12345, {"content": "# Updated"}).id  # doctest: +SKIP
            12345
        """
        return self._session.send(endpoints.update_page(page_id, body))

    def delete(self, page_id: int) -> PageDeleteResult:
        """``DELETE /pages/{id}`` → ``{recovery_token}``; keep the token to restore (undo).

        The returned :class:`PageDeleteResult` carries the ``recovery_token`` — the only handle
        to undo this delete, via ``RecoveryClient.restore`` (POST /recovery_tokens/{token}/recover).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.delete(12345).recovery_token  # doctest: +SKIP
            'a1b2c3d4-…'
        """
        return self._session.send(endpoints.delete_page(page_id))

    def append_content(self, page_id: int, body: dict[str, Any]) -> PageDetails:
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
        return self._session.send(endpoints.append_content(page_id, body))

    def clone(self, page_id: int, body: dict[str, Any]) -> PageCloneOperation:
        """``POST /pages/{id}/clone`` — copy the page to a new address (async trigger).

        Returns a :class:`PageCloneOperation`; poll its ``operation.id`` via
        ``OperationsClient.clone_get`` until terminal. ``body`` is a dumped :class:`PageClone`
        (``{target, title?, subscribe_me}``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.clone(12345, {"target": "data/y"}).operation.id  # doctest: +SKIP
            'task-1'
        """
        return self._session.send(endpoints.clone_page(page_id, body))
