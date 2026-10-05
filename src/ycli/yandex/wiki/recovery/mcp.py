"""Wiki /recovery_tokens FastMCP tool — restore a deleted page by its recovery token."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import WRITE, wiki_client
from ycli.yandex.wiki.recovery.models import RecoveredPage

mcp = FastMCP("wiki-recovery")


@mcp.tool(
    name="recovery_recover",
    annotations={**WRITE, "title": "Restore deleted Wiki page"},
)
def recover(
    token: Annotated[
        str, Field(description="UUID4 ``recovery_token`` returned by ``pages_delete``.")
    ],
    client: WikiClient = Depends(wiki_client),
) -> RecoveredPage:
    """Undo a page delete: redeem a ``recovery_token`` and bring the page back.

    ``pages_delete`` returns the token — it is the only handle to the deleted page. Returns
    the restored page's numeric ``id`` and permanent ``slug``, and ``pages_count``, how many pages
    came back (the page and those under it). No request body; the token in
    the path is the whole request.
    """
    return client.recovery.recover(token)
