"""Wiki ``/search`` client on the httpx2 core — full-text search over pages and files."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.search import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.search.models import SearchPage


class SearchClient(Resource):
    """``/search``: one page of full-text results per call."""

    def query(self, body: dict[str, Any]) -> SearchPage:
        """``POST /search`` → one :class:`SearchPage` of hits for the query.

        ``body`` is a dumped :class:`SearchRequest` (``query``, optional ``filters``, ``cursor``,
        ``limit``, ``order_by``, ``highlight``). Pages are walked by hand: ``next_cursor`` is the
        next page's number as text, but the API also sets it after an empty page and repeats
        hits for a page past the last one, so there is no reliable end to drain to. Stop at the
        first page with no results or when ``next_cursor`` is ``None``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> page = client.search.query({"query": "roadmap", "limit": 20})  # doctest: +SKIP
            >>> page.results[0].slug, page.next_cursor  # doctest: +SKIP
            ('team/roadmap', '2')
        """
        return self._session.send(endpoints.search_pages(body))
