"""Models for `ycli auth status` and the `status_get` MCP tool."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.account import Account  # noqa: TC001  # pydantic resolves field types at runtime
from ycli.yandex.models import APIModel


class ServiceAuthStatus(APIModel):
    """One service's auth probe: the account the token belongs to, or why the probe failed."""

    service: str
    valid: bool = False
    account: Account | None = None
    detail: str = ""


class AuthReport(APIModel):
    """Whether the credentials are set and work, per registered service."""

    configured: bool
    organization_id: str = ""
    services: list[ServiceAuthStatus] = Field(default_factory=list)
