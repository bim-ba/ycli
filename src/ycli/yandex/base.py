"""``DomainClient`` — the shared constructor of the domain composition roots (Tracker, Wiki, Forms).

A domain client opens one httpx2 core session for its service and hands it to every resource
client in :meth:`DomainClient._wire`. Credentials arrive as explicit constructor arguments
(ARCH-7): the base never reads the environment, and refuses an empty credential rather than
send an unauthenticated request.

Examples:
    >>> with tracker as client:
    ...     client.issues.get("DE-7").key
    'DE-7'
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Self

from pydantic import SecretStr

from ycli.settings import CLOUD_ORGANIZATION_ID_ENV, ORGANIZATION_ID_ENV, HTTPConfig

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType

    import httpx2

    from ycli.yandex.core.endpoint import Endpoint, Paged
    from ycli.yandex.core.profile import ServiceProfile
    from ycli.yandex.core.session import BeforeSend, SyncSession


class DomainClient(ABC):
    """One service's resource clients over one core session; a subclass wires and probes them.

    Sign in with ``oauth_token=`` (a Yandex ID OAuth token), or with ``auth=`` for anything
    else: :class:`~ycli.yandex.core.auth.IAMTokenAuth`, ``ServiceAccountAuth`` or your own
    ``httpx2.Auth``. ``profile`` is the service's
    :class:`~ycli.yandex.core.profile.ServiceProfile`; of ``organization_id`` (Yandex 360) and
    ``cloud_organization_id`` (Yandex Cloud) the service takes the kind it lives in. ``http``
    defaults to :class:`~ycli.settings.HTTPConfig`'s own defaults, so there is no second copy of
    them here; ``transport`` replaces the network (tests); ``before_send`` is called once per
    endpoint, before its first attempt, with its effect and request (a surface's seam to confirm
    or refuse a write; ``None`` for none, as the SDK and the MCP server leave it). What it
    returns is sent instead of the request; returning ``None`` sends the request unchanged.
    Leaving a ``with`` block, or :meth:`close`, closes the connection pool.
    """

    profile: ClassVar[ServiceProfile]

    def __init__(
        self,
        *,
        oauth_token: str | None = None,
        auth: httpx2.Auth | None = None,
        organization_id: str | None = None,
        cloud_organization_id: str | None = None,
        http: HTTPConfig | None = None,
        transport: httpx2.BaseTransport | None = None,
        before_send: BeforeSend | None = None,
    ) -> None:
        if bool(oauth_token) == (auth is not None):
            raise ValueError("pass an OAuth token or an auth, one of the two")
        kinds = (
            (self.profile.org_header, organization_id, ORGANIZATION_ID_ENV),
            (self.profile.cloud_org_header, cloud_organization_id, CLOUD_ORGANIZATION_ID_ENV),
        )
        taken = [variable for header, _, variable in kinds if header]
        if taken and not any(header and value for header, value, _ in kinds):
            raise ValueError(
                f"{type(self).__name__} needs an organization: set {' or '.join(taken)}"
            )
        # Imported here: httpx2 costs ~0.2 s, paid only once a domain client is built.
        from ycli.yandex.core.auth import OAuthTokenAuth
        from ycli.yandex.core.session import connect

        self._session = connect(
            self.profile,
            auth=auth or OAuthTokenAuth(SecretStr(oauth_token or "")),
            organization_id=organization_id,
            cloud_organization_id=cloud_organization_id,
            http=http or HTTPConfig(),
            transport=transport,
            before_send=before_send,
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

    def send[T](self, endpoint: Endpoint[T]) -> T:
        """Call any ``endpoint`` of this service through its session: auth, retries, errors, logs.

        The door for a request no resource client wraps (``ycli api``).
        """
        return self._session.send(endpoint)

    def iterate[P, I](self, paged: Paged[P, I], *, limit: int | None = None) -> Iterator[I]:
        """Yield the items of any ``paged`` listing of this service, at most ``limit``."""
        return self._session.iterate(paged, limit=limit)

    @abstractmethod
    def probe(self) -> None:
        """One cheap authenticated read: returns when the token works for this service.

        A rejected token raises :class:`~ycli.yandex.errors.YandexAuthError`; ``ycli auth
        status`` calls this for every service in the registry.
        """

    @abstractmethod
    def _wire(self, session: SyncSession) -> None:
        """Attach the per-resource clients over the shared ``session`` (per domain)."""
