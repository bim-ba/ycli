"""Cached tracker MCP client provider (see ycli.yandex.mcp.make_cached_client)."""

from ycli.yandex.mcp import RO, app_config, make_cached_client
from ycli.yandex.tracker.client import TrackerClient

TAGS: set[str] = {"tracker"}
tracker_client = make_cached_client(TrackerClient)

__all__ = ["RO", "TAGS", "app_config", "tracker_client"]
