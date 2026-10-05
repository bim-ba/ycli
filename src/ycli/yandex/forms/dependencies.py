"""Per-request forms MCP client provider (see ycli.yandex.mcp.client_provider)."""

from typing import Annotated

from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.mcp import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    OverBudget,
    app_config,
    client_provider,
)

TAGS: set[str] = {"forms"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
forms_client = client_provider(FormsClient)

SurveyID = Annotated[str, Field(description="Form id (24-char hex), from ``surveys_list``.")]

__all__ = [
    "DESTRUCTIVE",
    "LIMIT_CAP",
    "RO",
    "TAGS",
    "WRITE",
    "WRITE_IDEMPOTENT",
    "WRITE_TAGS",
    "OverBudget",
    "SurveyID",
    "app_config",
    "forms_client",
]
HookID = Annotated[int, Field(description="Integration group id (integer) from hooks_list.")]
