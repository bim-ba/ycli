"""Per-request DataLens MCP client provider (see ycli.yandex.mcp.client_provider)."""

from typing import Annotated

from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.mcp import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    All,
    Next,
    OverBudget,
    app_config,
    client_provider,
    new_server,
)

TAGS: set[str] = {"datalens"}
PermissionsInfo = Annotated[
    bool | None, Field(description="Also say what the caller may do with it.")
]
EntryID = Annotated[str, Field(description="Entry id.")]
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
    "All",
    "EntryID",
    "Next",
    "OverBudget",
    "PermissionsInfo",
    "app_config",
    "datalens_client",
    "new_server",
]
