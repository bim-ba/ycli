"""Wiki /pages/{id}/comments FastMCP tool."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

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
