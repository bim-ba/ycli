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

import copy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Self

from pydantic import SecretStr

from ycli.settings import CLOUD_ORGANIZATION_ID_ENV, ORGANIZATION_ID_ENV, HTTPConfig
from ycli.yandex.errors import YandexInvalidRequestError

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType

    import httpx2

    from ycli.yandex.core.endpoint import Endpoint, Paged
    from ycli.yandex.core.guard import Guard, PlannedRequest
    from ycli.yandex.core.listing import Listing
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
    them here; ``transport`` replaces the network (tests). ``guard`` shows or confirms a write
    before it is sent (:class:`~ycli.yandex.core.guard.Guard`; ``None`` sends everything).
    ``before_send`` is called once per endpoint, before its first attempt and before the guard,
    with its effect and request: what it returns is sent instead of the request, and ``None``
    sends the request unchanged (the CLI adds ``-F`` and ``--body-file`` to a body with it).
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
        guard: Guard | None = None,
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
            guard=guard,
        )
        self._wire(self._session)
        #: A view made by :meth:`with_options` shares the session of the client it came from.
        self._owns_session = True

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
        """Close the core session's connection pool; a view of a client has none of its own."""
        if self._owns_session:
            self._session.close()

    def with_options(
        self,
        *,
        timeout_seconds: float | None = None,
        retries: int | None = None,
        dry_run: bool | None = None,
    ) -> Self:
        """This client with other options, for the calls made through what is returned.

        A view of this client: the same connections and the same credentials, so nothing is
        opened and there is nothing of its own to close.

        Args:
            timeout_seconds: The timeout of each request; ``None`` keeps this client's.
            retries: How many times an idempotent request is tried again; ``None`` keeps it.
            dry_run: Whether a write is stopped and raised as
                :class:`~ycli.yandex.core.guard.RequestPlanned` in place of being sent
                (:meth:`plan` returns it as a value); ``None`` keeps what this client does.

        Returns:
            The client to make those calls through.

        Examples:
            >>> patient = tracker.with_options(timeout_seconds=120, retries=5)
            >>> patient.issues.get("DE-7").key
            'DE-7'
        """
        view = copy.copy(self)
        view._session = self._session.with_options(
            timeout_seconds=timeout_seconds, retries=retries, dry_run=dry_run
        )
        view._wire(view._session)
        view._owns_session = False
        return view

    def plan(self, call: Callable[[Self], object]) -> PlannedRequest:
        """The first write ``call`` would send, not sent: ``client -> the request``.

        ``call`` is given this client under ``dry_run`` and makes its calls through it. What it
        reads before its first write is read for real; the write is stopped and returned, and
        nothing after it runs. The plan says whether the request would grant access
        (``grants_access``).

        Args:
            call: What to plan, as a function of the client: ``lambda tracker: ...``.

        Returns:
            The request that would have gone out: its method, its URL and its body, with
            secrets masked.

        Raises:
            YandexInvalidRequestError: ``call`` sent no write: there is nothing to plan.

        Examples:
            >>> planned = tracker.plan(lambda tracker: tracker.boards.delete(31))
            >>> planned.method, planned.url.endswith("/v3/boards/31"), planned.grants_access
            ('DELETE', True, False)
            >>> tracker.plan(lambda tracker: tracker.boards.get(31))
            Traceback (most recent call last):
            ycli.yandex.errors.YandexInvalidRequestError: the call sends no write: nothing to plan
        """
        # Imported here, like the rest of the core: httpx2 is paid for once a client is built.
        from ycli.yandex.core.guard import RequestPlanned

        try:
            call(self.with_options(dry_run=True))
        except RequestPlanned as planned:
            return planned.plan
        # violation(arch-9): the caller asked for the plan of a call that writes nothing
        raise YandexInvalidRequestError("the call sends no write: nothing to plan")

    def send[T](self, endpoint: Endpoint[T]) -> T:
        """Call any ``endpoint`` of this service through its session: auth, retries, errors, logs.

        The door for a request no resource client wraps (``ycli api``).
        """
        return self._session.send(endpoint)

    def iterate[P, I](
        self,
        paged: Paged[P, I],
        *,
        limit: int | None = None,
        next: str | None = None,
    ) -> Listing[I]:
        """The items of any ``paged`` listing of this service: at most ``limit``, from ``next``."""
        return self._session.iterate(paged, limit=limit, next=next)

    @abstractmethod
    def probe(self) -> None:
        """One cheap authenticated read: returns when the token works for this service.

        A rejected token raises :class:`~ycli.yandex.errors.YandexAuthError`; ``ycli auth
        status`` calls this for every service in the registry.
        """

    @abstractmethod
    def _wire(self, session: SyncSession) -> None:
        """Attach the per-resource clients over the shared ``session`` (per domain)."""
