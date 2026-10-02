"""``DomainClient`` — the shared constructor of the domain composition roots (Tracker, Wiki, Forms).

A domain client opens one httpx2 core session for its service and hands it to every resource
client in :meth:`DomainClient._wire`. Credentials arrive as explicit constructor arguments
(ARCH-7): the base never reads the environment, and refuses an empty credential rather than
send an unauthenticated request.

Example:
    >>> with TrackerClient(oauth_token="…", organization_id="…") as client:  # doctest: +SKIP
    ...     client.issues.get("DE-1")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self

from pydantic import SecretStr

from ycli.settings import HTTPConfig

if TYPE_CHECKING:
    from types import TracebackType

    import httpx2

    from ycli.yandex.core.profile import ServiceProfile
    from ycli.yandex.core.session import SyncSession


class DomainClient:
    """One service's resource clients over one core session; a subclass declares only ``_wire``.

    ``profile`` is the service's :class:`~ycli.yandex.core.profile.ServiceProfile`. ``http``
    defaults to :class:`~ycli.settings.HTTPConfig`'s own defaults, so there is no second copy of
    them here; ``transport`` replaces the network (tests). Leaving a ``with`` block, or
    :meth:`close`, closes the connection pool.
    """

    profile: ClassVar[ServiceProfile]

    def __init__(
        self,
        *,
        oauth_token: str,
        organization_id: str,
        http: HTTPConfig | None = None,
        transport: httpx2.BaseTransport | None = None,
    ) -> None:
        if not oauth_token or not organization_id:
            raise ValueError("an OAuth token and an organization id are both required")
        self._session = self._connect(
            SecretStr(oauth_token), organization_id, http or HTTPConfig(), transport
        )
        self._wire(self._session)

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
        """Close the core session's connection pool."""
        self._session.close()

    def _connect(
        self,
        oauth_token: SecretStr,
        organization_id: str,
        http: HTTPConfig,
        transport: httpx2.BaseTransport | None,
    ) -> SyncSession:
        # Imported here: httpx2 costs ~0.2 s, paid only once a domain client is built.
        from ycli.yandex.core.auth import OAuthTokenAuth
        from ycli.yandex.core.session import connect

        return connect(
            self.profile,
            auth=OAuthTokenAuth(oauth_token),
            organization_id=organization_id,
            http=http,
            transport=transport,
        )

    def _wire(self, session: SyncSession) -> None:
        """Attach the per-resource clients over the shared ``session`` (per domain)."""
        raise NotImplementedError
