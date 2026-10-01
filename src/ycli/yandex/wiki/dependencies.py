"""Per-request wiki MCP client provider (see ycli.yandex.mcp.client_provider)."""

from ycli.yandex.mcp import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    app_config,
    client_provider,
)
from ycli.yandex.wiki.client import WikiClient

TAGS: set[str] = {"wiki"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
wiki_client = client_provider(WikiClient)

__all__ = [
    "DESTRUCTIVE",
    "RO",
    "TAGS",
    "WRITE",
    "WRITE_IDEMPOTENT",
    "WRITE_TAGS",
    "app_config",
    "wiki_client",
]
