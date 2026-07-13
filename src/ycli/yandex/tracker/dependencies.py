"""Cached tracker MCP client provider (see ycli.yandex.mcp.make_cached_client)."""

from ycli.yandex.mcp import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    app_config,
    make_cached_client,
)
from ycli.yandex.tracker.client import TrackerClient

TAGS: set[str] = {"tracker"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
tracker_client = make_cached_client(TrackerClient)

__all__ = [
    "DESTRUCTIVE",
    "RO",
    "TAGS",
    "WRITE",
    "WRITE_IDEMPOTENT",
    "WRITE_TAGS",
    "app_config",
    "tracker_client",
]
