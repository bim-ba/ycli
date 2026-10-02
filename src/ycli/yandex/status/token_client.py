"""What a token says about itself: its owner (Yandex ID) and its organizations (API 360).

Both are ordinary authenticated GETs on the httpx2 core. Each host takes no organization
header, so each has a :class:`~ycli.yandex.core.profile.ServiceProfile` with ``org_header=None``
(ARCH-5). Credentials arrive as constructor arguments (ARCH-7).

Example:
    >>> with TokenClient(oauth_token="…") as client:  # doctest: +SKIP
    ...     client.identity().login
    'ivan'
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import SecretStr

from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.core.pagination import CursorPagination
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.core.session import connect
from ycli.yandex.status.models import Identity
from ycli.yandex.status.oauth_models import Organization, OrganizationList

if TYPE_CHECKING:
    from types import TracebackType

    import httpx2

    from ycli.settings import HTTPConfig

YANDEX_ID = ServiceProfile("https://login.yandex.ru", org_header=None)
API360 = ServiceProfile("https://api360.yandex.net", org_header=None)

ORGANIZATIONS_PAGE_SIZE = 100  # API 360's maximum


def _next_page_token(response: httpx2.Response) -> str | None:
    return response.json().get("nextPageToken")


GET_IDENTITY: Endpoint[Identity] = Endpoint("GET", "info", Identity, params={"format": "json"})
LIST_ORGANIZATIONS: Paged[OrganizationList, Organization] = Paged(
    Endpoint(
        "GET",
        "directory/v1/org",
        OrganizationList,
        params={"pageSize": ORGANIZATIONS_PAGE_SIZE},
    ),
    CursorPagination(cursor_of=_next_page_token, cursor_param="pageToken"),
    lambda page: page.organizations,
)


class TokenClient:
    """Reads the token's owner from Yandex ID and its organizations from API 360."""

    def __init__(
        self,
        *,
        oauth_token: str,
        http: HTTPConfig | None = None,
        transport: httpx2.BaseTransport | None = None,
    ) -> None:
        auth = OAuthTokenAuth(SecretStr(oauth_token))
        self._identity = connect(YANDEX_ID, auth=auth, http=http, transport=transport)
        self._directory = connect(API360, auth=auth, http=http, transport=transport)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close both connection pools."""
        self._identity.close()
        self._directory.close()

    def identity(self) -> Identity:
        """``GET /info`` — who owns the token. Any valid token answers; a rejected one raises."""
        return self._identity.send(GET_IDENTITY)

    def organizations(self) -> list[Organization]:
        """``GET /directory/v1/org`` — every organization the token can see, page by page.

        A token without the ``directory:read_organization`` scope raises ``YandexAuthError``
        (401 or 403).
        """
        return list(self._directory.iterate(LIST_ORGANIZATIONS))
