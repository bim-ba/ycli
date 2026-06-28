"""Cached forms MCP client provider (see ycli.yandex._mcp.make_cached_client)."""

from ycli.yandex._mcp import RO, app_config, make_cached_client
from ycli.yandex.forms.client import FormsClient

TAGS: set[str] = {"forms"}
forms_client = make_cached_client(FormsClient)

__all__ = ["RO", "TAGS", "app_config", "forms_client"]
