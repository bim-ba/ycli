"""Declarative Yandex Wiki /pages client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""
import uplink

from ycli.yandex.wiki._base import WikiResource
from ycli.yandex.wiki.pages.models import DescendantsResponse, PageDetails


class PagesClient(WikiResource):
    """Declarative HTTP for ``/pages`` (get, descendants, create, update)."""

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
    def descendants(
        self,
        slug: uplink.Query,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
        cursor: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        actuality: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> DescendantsResponse:  # ty: ignore[empty-body]
        """``GET /pages/descendants`` → one page of ``{id, slug}`` refs + ``next_cursor``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> page = client.pages.descendants(slug="data", page_size=50)  # doctest: +SKIP
            >>> page.results[0].slug, page.next_cursor  # doctest: +SKIP
            ('data/architecture', 'eyJvZmZzZXQiOjUwfQ==')
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("pages")
    def create(self, body: uplink.Body) -> PageDetails:  # ty: ignore[empty-body]
        """``POST /pages`` — create. ``body`` carries ``content``/``title``/``slug``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.pages.create({"slug": "data/guides/x", "title": "X", "content": "# X"}).id  # doctest: +SKIP
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
