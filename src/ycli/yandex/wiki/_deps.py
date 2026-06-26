"""FastMCP dependency provider for the wiki subserver — builds a WikiClient per call."""
from ycli.yandex.wiki.client import WikiClient

RO: dict[str, bool] = {"readOnlyHint": True}
TAGS: set[str] = {"wiki"}


def wiki_client() -> WikiClient:
    """Provide an env-built WikiClient to wiki MCP tools (FastMCP caches within a call)."""
    return WikiClient.from_env()
