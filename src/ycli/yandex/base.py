"""Shared base for every Yandex resource client (uplink.Consumer).

Holds the two things every resource repeats: a required-``session`` constructor (DI —
the client takes a configured ``requests.Session``, never reaches into the env) and a
``base_url`` ClassVar set by a per-domain base (e.g. ``WikiResource``); resource clients
inherit it.

uplink's ``ConsumerMeta`` collects decorated request methods from the leaf subclass, so
an intermediate base with no decorated methods is fine.

NOTE: no ``from __future__ import annotations`` — uplink reads method annotations eagerly.

Example:
    >>> from ycli.yandex.wiki.pages.client import PagesClient
    >>> import requests
    >>> client = PagesClient(session=requests.Session())  # doctest: +SKIP
"""

from typing import TYPE_CHECKING, ClassVar, Self

import requests
import uplink
from pydantic import SecretStr

from ycli.settings import HTTPConfig
from ycli.yandex.transport import Transport

if TYPE_CHECKING:
    from types import TracebackType

    import httpx2

    from ycli.yandex.core.profile import ServiceProfile
    from ycli.yandex.core.session import SyncSession


class BaseYandex(uplink.Consumer):
    """Required-``session`` DI + ``base_url`` classvar."""

    base_url: ClassVar[str]

    def __init__(self, *, session: requests.Session) -> None:
        base = self.base_url.rstrip("/") + "/"
        self._session: requests.Session = session
        super().__init__(base_url=base, client=session)


class DomainClient:
    """Shared constructor for the domain composition roots (Tracker / Wiki / Forms).

    Builds the authed ``requests.Session`` for the resources still on ``uplink`` and, through
    :meth:`_connect`, an httpx2 :class:`~ycli.yandex.core.session.SyncSession` for resources
    already on the core; a subclass declares ONLY its resource wiring in :meth:`_wire`.
    Credentials arrive as explicit constructor arguments (ARCH-7) — the base never reads the
    environment. ``http`` defaults to :class:`~ycli.settings.HTTPConfig`'s own defaults, so
    there is no second copy of them here. ``transport`` replaces the core's network (tests).
    :meth:`close` (or leaving a ``with`` block) closes both connection pools.
    """

    def __init__(
        self,
        *,
        oauth_token: str,
        organization_id: str,
        http: HTTPConfig | None = None,
        session: requests.Session | None = None,
        transport: "httpx2.BaseTransport | None" = None,
    ) -> None:
        self._oauth_token = SecretStr(oauth_token)
        self._organization_id = organization_id
        self._http = http or HTTPConfig()
        self._transport = transport
        self._core_sessions: list[SyncSession] = []
        self._session = Transport.session(
            oauth_token=oauth_token,
            organization_id=organization_id,
            timeout_seconds=self._http.timeout_seconds,
            retries=self._http.retries,
            base=session,
        )
        self._wire(self._session)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: "TracebackType | None",
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the requests session and every core session this client opened."""
        for core_session in self._core_sessions:
            core_session.close()
        self._session.close()

    def _connect(self, profile: "ServiceProfile") -> "SyncSession":
        """A core session to ``profile`` with this client's credentials and HTTP settings."""
        # Imported here: httpx2 costs ~0.2 s, paid only by a domain with a resource on the core.
        from ycli.yandex.core.auth import OAuthTokenAuth
        from ycli.yandex.core.session import connect

        core_session = connect(
            profile,
            auth=OAuthTokenAuth(self._oauth_token),
            organization_id=self._organization_id,
            http=self._http,
            transport=self._transport,
        )
        self._core_sessions.append(core_session)
        return core_session

    def _wire(self, transport: requests.Session) -> None:
        """Attach the per-resource clients over the shared ``transport`` (per-domain)."""
        raise NotImplementedError
