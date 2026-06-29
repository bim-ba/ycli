"""Cached forms MCP client provider (see ycli.yandex.mcp.make_cached_client)."""

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.mcp import RO, app_config, make_cached_client

TAGS: set[str] = {"forms"}
forms_client = make_cached_client(FormsClient)

__all__ = ["RO", "TAGS", "app_config", "forms_client"]
