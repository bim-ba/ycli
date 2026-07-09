"""Wiki /pages/{id}/comments FastMCP tools."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.comments.models import CommentList
from ycli.yandex.wiki.dependencies import RO, TAGS, app_config, wiki_client

mcp = FastMCP("wiki-comments")


@mcp.tool(name="comments_list", annotations={**RO, "title": "List Wiki comments"}, tags=TAGS)
def list_(
    page_id: int,
    limit: int = 0,
    client: WikiClient = Depends(wiki_client),
    cfg: AppConfig = Depends(app_config),
) -> CommentList:
    """Comments on a page id, auto-paginated (drains the ``next_cursor`` internally).

    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given. Pair with
    ``pages_meta`` (its ``attributes.comments_count`` tells you how many exist).
    """
    cap = limit or cfg.max_items
    return client.comments.list(page_id=page_id, limit=cap)


@mcp.tool(
    name="comments_thread_list", annotations={**RO, "title": "List Wiki comment thread"}, tags=TAGS
)
def thread_list(
    page_id: Annotated[int, Field(description="Numeric page id the comment lives on.")],
    comment_id: Annotated[int, Field(description="Root comment id whose reply thread to fetch.")],
    limit: Annotated[int, Field(description="Max replies (0 = YCLI_MAX_ITEMS cap).")] = 0,
    client: WikiClient = Depends(wiki_client),
    cfg: AppConfig = Depends(app_config),
) -> CommentList:
    """The reply thread rooted at a comment, auto-paginated (drains the ``next_cursor`` internally).

    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given. Use ``comments_list``
    first to discover a root comment id, then this to read its replies.

    Example:
        >>> thread_list(page_id=12345, comment_id=678, limit=50)  # doctest: +SKIP
    """
    cap = limit or cfg.max_items
    return client.comments.thread(page_id=page_id, comment_id=comment_id, limit=cap)
