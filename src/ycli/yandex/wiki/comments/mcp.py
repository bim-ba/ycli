"""Wiki /pages/{id}/comments FastMCP tool."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.wiki._deps import RO, TAGS, wiki_client
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.comments.models import CommentList

mcp = FastMCP("wiki-comments")


@mcp.tool(name="comments_list", annotations={**RO, "title": "List Wiki comments"}, tags=TAGS)
def list_(page_id: int, client: WikiClient = Depends(wiki_client)) -> CommentList:
    """Comments on a page id."""
    return client.comments.list(page_id=page_id)
