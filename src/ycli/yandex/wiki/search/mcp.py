"""Wiki /search FastMCP tool."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, wiki_client
from ycli.yandex.wiki.search.models import SearchFilters, SearchOrder, SearchPage, SearchRequest

mcp = FastMCP("wiki-search")


@mcp.tool(name="search_query", annotations={**RO, "title": "Search Wiki"})
def query(
    text: Annotated[str, Field(description="Text to search for.")],
    filters: Annotated[
        SearchFilters | None,
        Field(
            description="Narrow the search by ``type``, ``authors``, ``cluster`` (a page slug), "
            "``created_at`` / ``modified_at`` (a window with both ``from`` and ``to``) and "
            "``show_obsolete``."
        ),
    ] = None,
    order_by: Annotated[SearchOrder, Field(description="How to sort the hits.")] = "relevancy",
    highlight: Annotated[
        bool, Field(description="Wrap the matches in ``<em>`` tags in title and content.")
    ] = False,
    limit: Annotated[int, Field(description="Hits per page.")] = 10,
    cursor: Annotated[int, Field(description="Number of the result page to fetch, from 1.")] = 1,
    client: WikiClient = Depends(wiki_client),
) -> SearchPage:
    """Full-text search over wiki pages and files; returns one page of hits.

    Each hit has the page ``slug`` (read it with ``pages_get``), ``title``, a ``content``
    snippet, the ``type`` and ``modified_at``. For the next page pass ``next_cursor`` back as
    ``cursor``; stop at the first page without hits, because ``next_cursor`` stays set after an
    empty page. A new page can take seconds to appear in the index.
    """
    request = SearchRequest(
        query=text,
        filters=filters,
        cursor=cursor,
        limit=limit,
        order_by=order_by,
        highlight=highlight,
    )
    return client.search.query(request)
