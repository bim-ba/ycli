"""Per-request DataLens MCP client provider (see ycli.yandex.mcp.client_provider)."""

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.mcp import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    app_config,
    client_provider,
)

TAGS: set[str] = {"datalens"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
datalens_client = client_provider(DataLensClient)

__all__ = [
    "DESTRUCTIVE",
    "LIMIT_CAP",
    "RO",
    "TAGS",
    "WRITE",
    "WRITE_IDEMPOTENT",
    "WRITE_TAGS",
    "app_config",
    "datalens_client",
]
