"""Wiki /pages/{id}/attachments FastMCP tool."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.wiki._deps import RO, TAGS, wiki_client
from ycli.yandex.wiki.attachments.models import AttachmentList
from ycli.yandex.wiki.client import WikiClient

mcp = FastMCP("wiki-attachments")


@mcp.tool(name="attachments_list", annotations={**RO, "title": "List Wiki attachments"}, tags=TAGS)
def list_(page_id: int, client: WikiClient = Depends(wiki_client)) -> AttachmentList:
    """Attachments on a page id."""
    return client.attachments.list(page_id=page_id)
