"""Per-request forms MCP client provider (see ycli.yandex.mcp.client_provider)."""

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.mcp import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    app_config,
    client_provider,
)

TAGS: set[str] = {"forms"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
forms_client = client_provider(FormsClient)

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
