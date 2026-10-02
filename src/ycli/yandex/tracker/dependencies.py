"""Per-request tracker MCP client provider (see ycli.yandex.mcp.client_provider)."""

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
from ycli.yandex.tracker.client import TrackerClient

TAGS: set[str] = {"tracker"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
tracker_client = client_provider(TrackerClient)

__all__ = [
    "DESTRUCTIVE",
    "LIMIT_CAP",
    "RO",
    "TAGS",
    "WRITE",
    "WRITE_IDEMPOTENT",
    "WRITE_TAGS",
    "app_config",
    "tracker_client",
]
