"""Wiki /users/me FastMCP tool (read-only) — Depends DI."""

from fastmcp.dependencies import Depends

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, new_server, wiki_client
from ycli.yandex.wiki.me.models import Me

mcp = new_server("wiki-me")


@mcp.tool(name="me_get", annotations={**RO, "title": "Get current Wiki user"})
def get(client: WikiClient = Depends(wiki_client)) -> Me:
    """The authenticated Yandex Wiki user (a safe auth probe)."""
    return client.me.get()
