"""``ServiceProfile`` — where a service lives and which headers name the organization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

# Yandex 360's organization header — the single place this name is spelled (ARCH-5).
ORG_HEADER = "X-Org-Id"
# The header of a Yandex Cloud organization, for the services that live in either kind.
CLOUD_ORG_HEADER = "X-Cloud-Org-Id"


@dataclass(frozen=True, slots=True)
class ServiceProfile:
    """A service's base URL, its organization headers and any fixed headers it requires.

    A service names the organization by its kind: ``org_header`` takes a Yandex 360 organization
    (``X-Org-Id``), ``cloud_org_header`` a Yandex Cloud one (``X-Cloud-Org-Id``; ``x-dl-org-id``
    for DataLens). A service that lives in one kind only leaves the other header ``None``; some
    (Maps) take none. ``oauth_token`` is whether the service takes a Yandex ID OAuth token:
    DataLens takes an IAM token only.

    Examples:
        >>> ServiceProfile("https://api.example.net/v1").headers_for("org-1")
        {'X-Org-Id': 'org-1'}
        >>> ServiceProfile("https://api.example.net/v1").headers_for(None, "cloud-1")
        {'X-Cloud-Org-Id': 'cloud-1'}
    """

    base_url: str
    org_header: str | None = ORG_HEADER
    cloud_org_header: str | None = CLOUD_ORG_HEADER
    headers: Mapping[str, str] = field(default_factory=dict)
    oauth_token: bool = True

    def headers_for(
        self, organization_id: str | None, cloud_organization_id: str | None = None
    ) -> dict[str, str]:
        """The default headers of every request to this service.

        One organization header at most: the Yandex 360 one when the service takes it and the id
        is given, else the Yandex Cloud one.

        Args:
            organization_id: The Yandex 360 organization, when configured.
            cloud_organization_id: The Yandex Cloud organization, when configured.

        Returns:
            The fixed headers plus the one organization header.
        """
        headers = dict(self.headers)
        if self.org_header and organization_id:
            headers[self.org_header] = organization_id
        elif self.cloud_org_header and cloud_organization_id:
            headers[self.cloud_org_header] = cloud_organization_id
        return headers

    def organization(
        self, organization_id: str | None, cloud_organization_id: str | None = None
    ) -> str:
        """The organization :meth:`headers_for` names to this service, with the header it is in.

        The header is a part of it: organization ``7`` of Yandex 360 and organization ``7`` of
        Yandex Cloud are two organizations. Empty when the service is named none.

        Args:
            organization_id: The Yandex 360 organization, when configured.
            cloud_organization_id: The Yandex Cloud organization, when configured.

        Returns:
            The one organization header as ``Name: id``, or ``""``.

        Examples:
            >>> ServiceProfile("https://x").organization("org-1", "cloud-1")
            'X-Org-Id: org-1'
            >>> ServiceProfile("https://x", org_header=None).organization("org-1", "cloud-1")
            'X-Cloud-Org-Id: cloud-1'
            >>> ServiceProfile("https://x").organization(None)
            ''
        """
        named = set(self.headers_for(organization_id, cloud_organization_id).items())
        return "".join(f"{name}: {value}" for name, value in named - set(self.headers.items()))
