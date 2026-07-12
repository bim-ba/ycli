"""Cached forms MCP client provider (see ycli.yandex.mcp.make_cached_client)."""

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.mcp import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    app_config,
    make_cached_client,
)

TAGS: set[str] = {"forms"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
forms_client = make_cached_client(FormsClient)

__all__ = [
    "DESTRUCTIVE",
    "RO",
    "TAGS",
    "WRITE",
    "WRITE_IDEMPOTENT",
    "WRITE_TAGS",
    "app_config",
    "forms_client",
]
