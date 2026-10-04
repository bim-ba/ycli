"""Pydantic models for Wiki full-text search (``POST /search``).

Replies keep unknown fields (:class:`~ycli.yandex.models.APIModel`); request bodies refuse them.
"""

from __future__ import annotations

from datetime import datetime  # pydantic reads the field type at runtime
from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.wiki.models import UserIdentity

#: What a search hit is.
SearchDocumentType = Literal["page", "file"] | str
#: How hits are sorted.
SearchOrder = Literal["relevancy", "creation_date", "modified_date"] | str


class SearchDateRange(RequestBody):
    """A time window for ``created_at`` / ``modified_at``; both ends are required.

    The spec calls both ends optional, but the live API answers an open-ended window with
    ``400 SEARCH_BAD_REQUEST``, so a missing end fails here instead.

    Examples:
        >>> SearchDateRange(start="2026-01-01", end="2026-02-01").model_dump(mode="json")
        {'from': '2026-01-01T00:00:00', 'to': '2026-02-01T00:00:00'}
    """

    start: datetime = Field(alias="from", description="Start of the window (ISO 8601).")
    end: datetime = Field(alias="to", description="End of the window (ISO 8601).")


class SearchFilters(RequestBody):
    """What to narrow a search to; every filter is optional.

    Examples:
        >>> SearchFilters(type="page", cluster="docs").model_dump(exclude_none=True)
        {'type': 'page', 'cluster': 'docs', 'show_obsolete': False}
    """

    type: SearchDocumentType | None = Field(default=None, description="Only pages or only files.")
    authors: list[UserIdentity] | None = Field(
        default=None, description="Only documents by these users (uid or cloud_uid)."
    )
    cluster: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Only documents under this page slug, e.g. ``team/handbook``.",
    )
    created_at: SearchDateRange | None = Field(
        default=None, description="Only documents created in this window."
    )
    modified_at: SearchDateRange | None = Field(
        default=None, description="Only documents modified in this window."
    )
    show_obsolete: bool = Field(
        default=False, description="Also return obsolete (outdated) documents."
    )


class SearchRequest(RequestBody):
    """Body of ``POST /search``: the query, filters and one page of the results.

    Examples:
        >>> SearchRequest(query="roadmap", limit=5).model_dump(exclude_none=True)
        {'query': 'roadmap', 'cursor': 1, 'limit': 5, 'order_by': 'relevancy', 'highlight': False}
    """

    query: str = Field(min_length=1, description="Text to search for.")
    filters: SearchFilters | None = Field(default=None, description="Narrow the search.")
    cursor: int = Field(default=1, ge=1, le=500, description="Number of the result page, from 1.")
    limit: int = Field(default=10, ge=1, le=50, description="Results per page.")
    order_by: SearchOrder = Field(default="relevancy", description="How to sort the results.")
    highlight: bool = Field(
        default=False, description="Wrap the matches in ``<em>`` tags in title and content."
    )


class SearchResult(APIModel):
    """One hit of a search.

    Examples:
        >>> SearchResult.model_validate({"slug": "docs/a", "title": "A"}).slug
        'docs/a'
    """

    url: str | None = Field(default=None, description="Path of the document on the Wiki.")
    slug: str | None = Field(default=None, description="Slug of the page the hit belongs to.")
    title: str | None = Field(default=None, description="Title, with matches in ``<em>`` if asked.")
    content: str | None = Field(default=None, description="Snippet of the matching text.")
    type: SearchDocumentType | None = Field(default=None, description="Page or file.")
    modified_at: str | None = Field(
        default=None, description="Time of the last change, as the API prints it."
    )


class SearchPage(APIModel):
    """One page of search results.

    ``next_cursor`` is the number of the following page as text (``"2"``), to pass back as the
    next request's ``cursor``. The API sets it even after a page with no results, so do not
    page until it is ``null``: stop at the first empty page.

    Examples:
        >>> SearchPage.model_validate({"results": [], "next_cursor": "2"}).next_cursor
        '2'
    """

    results: list[SearchResult] = Field(default_factory=list, description="Hits on this page.")
    next_cursor: str | None = Field(
        default=None, description="Cursor of the next page, or ``null`` when there is none."
    )
    prev_cursor: str | None = Field(
        default=None, description="Cursor of the previous page, or ``null`` on the first."
    )
