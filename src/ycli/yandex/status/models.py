"""Models for `ycli auth status` and the `status_get` MCP tool."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.forms.me.models import (
    User as FormsMe,  # noqa: TC001  # pydantic resolves field types via get_type_hints() at runtime
)
from ycli.yandex.models import APIModel
from ycli.yandex.tracker.me.models import (
    Me as TrackerMe,  # noqa: TC001  # pydantic resolves field types via get_type_hints() at runtime
)
from ycli.yandex.wiki.me.models import (
    Me as WikiMe,  # noqa: TC001  # pydantic resolves field types via get_type_hints() at runtime
)


class ServiceAuthStatus(APIModel):
    """One service's auth probe — the bare native `me` on success, else why it failed."""

    service: str
    valid: bool = False
    me: TrackerMe | WikiMe | FormsMe | None = None
    detail: str = ""


class AuthReport(APIModel):
    """Whether the env credentials are set and work, per service."""

    configured: bool
    organization_id: str = ""
    services: list[ServiceAuthStatus] = Field(default_factory=list)
