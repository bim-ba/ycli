"""Wiki /users/me FastMCP tool (read-only) — Depends DI."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.settings import OAUTH_TOKEN_ENV
from ycli.yandex.models import require_found
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, wiki_client
from ycli.yandex.wiki.me.models import Me

mcp = FastMCP("wiki-me")


@mcp.tool(name="me_get", annotations={**RO, "title": "Get current Wiki user"})
def get(client: WikiClient = Depends(wiki_client)) -> Me:
    """The authenticated Yandex Wiki user (a safe auth probe)."""
    result = client.me.get()
    return require_found(
        result,
        sentinel=lambda r: r.username is None,
        message=f"auth probe failed — empty user (check {OAUTH_TOKEN_ENV})",
    )
