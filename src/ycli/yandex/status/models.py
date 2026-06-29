"""Models for `ycli auth status` and the `status_get` MCP tool.

The per-service `me` payloads (Tracker/Wiki/Forms) are all-optional and ignore extras,
so an *undiscriminated* ``me`` union is ambiguous: every payload validates against every
member. fastmcp rebuilds ``result.data`` from the tool's output JSON schema and, on an
undiscriminated ``anyOf``, picks the first matching branch — silently reshaping a wiki
payload into the tracker shape and dropping fields like ``username``. Tagging each status
with a ``Literal`` ``service`` discriminator makes the schema self-describing, so the
round-trip stays loss-free. The CLI/SDK path keeps the bare native ``me`` model instance.
"""

from __future__ import annotations

from typing import Annotated, Literal

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


class _ServiceAuthStatus(APIModel):
    """One service's auth probe — the bare native `me` on success, else why it failed.

    Subclasses narrow ``service`` to a ``Literal`` tag (the union discriminator) and ``me``
    to that service's model; field order is preserved through the overrides.
    """

    service: str
    valid: bool = False
    me: TrackerMe | WikiMe | FormsMe | None = None
    detail: str = ""


class TrackerAuthStatus(_ServiceAuthStatus):
    service: Literal["tracker"] = "tracker"
    me: TrackerMe | None = None


class WikiAuthStatus(_ServiceAuthStatus):
    service: Literal["wiki"] = "wiki"
    me: WikiMe | None = None


class FormsAuthStatus(_ServiceAuthStatus):
    service: Literal["forms"] = "forms"
    me: FormsMe | None = None


ServiceAuthStatus = Annotated[
    TrackerAuthStatus | WikiAuthStatus | FormsAuthStatus, Field(discriminator="service")
]


class AuthReport(APIModel):
    """Whether the env credentials are set and work, per service."""

    configured: bool
    organization_id: str = ""
    services: list[ServiceAuthStatus] = Field(default_factory=list)
