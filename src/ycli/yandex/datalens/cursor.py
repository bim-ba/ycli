"""How a DataLens listing pages: ``nextPageToken`` in the reply, sent back in the body.

Most listings take it back as ``pageToken``; the content of a collection takes it as ``page``.

Examples:
    >>> import httpx2
    >>> next_page_token(httpx2.Response(200, json={"items": [], "nextPageToken": "t2"}))
    't2'
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.pagination import BodyCursorPagination

if TYPE_CHECKING:
    import httpx2


def next_page_token(response: httpx2.Response) -> str | None:
    """The page's ``nextPageToken`` (absent or empty once the listing is exhausted)."""
    return response.json().get("nextPageToken")


DATALENS_CURSOR = BodyCursorPagination(cursor_of=next_page_token)
