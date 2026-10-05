"""How a DataLens listing pages: ``nextPageToken`` in the reply, sent back in the body.

Most listings take it back as ``pageToken``; the content of a collection takes it as ``page``.
The listings of workbooks and of a workbook's entries take ``page`` as a number: the token
comes as the string ``"1"`` and the API refuses it unless it is sent back as ``1`` (measured).

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


def next_page_number(response: httpx2.Response) -> int | None:
    """The page's ``nextPageToken`` as the number the next request must carry.

    Args:
        response: The page just read.

    Returns:
        The number of the next page; ``None`` once the listing is exhausted.

    Examples:
        >>> import httpx2
        >>> next_page_number(httpx2.Response(200, json={"nextPageToken": "1"}))
        1
    """
    token = next_page_token(response)
    return int(token) if token else None


DATALENS_CURSOR = BodyCursorPagination(cursor_of=next_page_token)
DATALENS_PAGE_NUMBER = BodyCursorPagination(cursor_of=next_page_number, cursor_param="page")
