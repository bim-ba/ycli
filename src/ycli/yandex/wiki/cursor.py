"""How every Wiki listing pages: ``next_cursor`` in the body, sent back as ``?cursor=``.

Example:
    >>> import httpx2
    >>> next_cursor(httpx2.Response(200, json={"results": [], "next_cursor": "c2"}))
    'c2'
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.pagination import CursorPagination

if TYPE_CHECKING:
    import httpx2


def next_cursor(response: httpx2.Response) -> str | None:
    """The page's ``next_cursor`` (``null`` once the listing is exhausted)."""
    return response.json().get("next_cursor")


WIKI_CURSOR = CursorPagination(cursor_of=next_cursor)
