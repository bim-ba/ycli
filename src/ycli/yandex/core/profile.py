"""``ServiceProfile`` — where a service lives and which header names the organization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

# Yandex 360's organization header — the single place this name is spelled (ARCH-5).
ORG_HEADER = "X-Org-Id"


@dataclass(frozen=True, slots=True)
class ServiceProfile:
    """A service's base URL, its organization header and any fixed headers it requires.

    Yandex services name the organization differently: ``X-Org-Id`` (Yandex 360),
    ``X-Cloud-Org-Id`` (Yandex Cloud organizations), ``x-dl-org-id`` plus
    ``x-dl-api-version`` (DataLens); some (Maps) take none.

    Example:
        >>> ServiceProfile("https://api.example.net/v1").headers_for("org-1")
        {'X-Org-Id': 'org-1'}
    """

    base_url: str
    org_header: str | None = ORG_HEADER
    headers: Mapping[str, str] = field(default_factory=dict)

    def headers_for(self, organization_id: str | None) -> dict[str, str]:
        """The default headers of every request to this service for ``organization_id``."""
        headers = dict(self.headers)
        if self.org_header and organization_id:
            headers[self.org_header] = organization_id
        return headers
