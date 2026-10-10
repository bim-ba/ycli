"""Per-request wiki MCP client provider (see ycli.yandex.mcp.client_provider)."""

from typing import Annotated

from pydantic import Field

from ycli.yandex.mcp import (
    DESTRUCTIVE,
    GRANTS_ACCESS,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    All,
    Next,
    app_config,
    client_provider,
    new_server,
)
from ycli.yandex.wiki.client import WikiClient

TAGS: set[str] = {"wiki"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
wiki_client = client_provider(WikiClient)

Slug = Annotated[str, Field(description="Wiki page slug (its path), e.g. ``users/something/abc``.")]
PageID = Annotated[
    int, Field(description="Numeric page id, from ``pages_get_meta`` or a page ref.")
]

__all__ = [
    "DESTRUCTIVE",
    "GRANTS_ACCESS",
    "LIMIT_CAP",
    "RO",
    "TAGS",
    "WRITE",
    "WRITE_IDEMPOTENT",
    "WRITE_TAGS",
    "All",
    "Next",
    "PageID",
    "Slug",
    "app_config",
    "new_server",
    "wiki_client",
]
