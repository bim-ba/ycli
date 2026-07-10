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

from typing import ClassVar

import requests
import uplink

from ycli.yandex.transport import Transport


class BaseYandex(uplink.Consumer):
    """Required-``session`` DI + ``base_url`` classvar."""

    base_url: ClassVar[str]

    def __init__(self, *, session: requests.Session) -> None:
        base = self.base_url.rstrip("/") + "/"
        self._session: requests.Session = session
        super().__init__(base_url=base, client=session)


class DomainClient:
    """Shared constructor for the three domain composition roots (Tracker / Wiki / Forms).

    Each domain client is a byte-identical container: build one authed ``requests.Session`` from
    the credentials + config, then wire the per-resource clients over it. This base owns the
    build; a subclass declares ONLY its resource wiring in :meth:`_wire`. Credentials arrive as
    explicit constructor arguments (ARCH-7) — the base never reads the environment.

    The ``timeout_seconds`` / ``retries`` defaults intentionally equal ``AppConfig``'s defaults
    (the ARCH-10 carve-out): they apply only when a caller passes nothing, and ``AppContext``
    always passes the configured value. A test pins ``inspect.signature`` of a domain client to
    those defaults, so this signature must stay in sync with ``AppConfig``.
    """

    def __init__(
        self,
        *,
        oauth_token: str,
        organization_id: str,
        timeout_seconds: int = 30,
        retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        self._wire(
            Transport.session(
                oauth_token=oauth_token,
                organization_id=organization_id,
                timeout_seconds=timeout_seconds,
                retries=retries,
                base=session,
            )
        )

    def _wire(self, transport: requests.Session) -> None:
        """Attach the per-resource clients over the shared ``transport`` (per-domain)."""
        raise NotImplementedError
