"""Wiki ``POST /search``, declared once (sans-IO).

The search is a ``POST`` that only reads, so it declares itself a read.

Examples:
    >>> search_pages({"query": "roadmap"}).effect
    'read'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.wiki.search.models import SearchPage, SearchRequest


def search_pages(body: SearchRequest) -> Endpoint[SearchPage]:
    return Endpoint("POST", "search", SearchPage, json=body, effect="read")
