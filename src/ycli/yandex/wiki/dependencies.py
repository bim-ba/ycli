"""Cached wiki MCP client provider (see ycli.yandex.mcp.make_cached_client)."""

from ycli.yandex.mcp import RO, app_config, make_cached_client
from ycli.yandex.wiki.client import WikiClient

TAGS: set[str] = {"wiki"}
wiki_client = make_cached_client(WikiClient)

__all__ = ["RO", "TAGS", "app_config", "wiki_client"]
