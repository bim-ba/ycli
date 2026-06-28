"""Shared base for every Yandex resource client (uplink.Consumer).

Holds the two things every resource repeats: a required-``session`` constructor (DI —
the client takes a configured ``requests.Session``, never reaches into the env) and a
``from_env()`` classmethod (via ``FromEnvSession`` mixin). The per-API base URL is a
``base_url`` ClassVar set by a per-domain base (e.g. ``WikiResource``); resource clients
inherit it.

uplink's ``ConsumerMeta`` collects decorated request methods from the leaf subclass, so
an intermediate base with no decorated methods is fine.

NOTE: no ``from __future__ import annotations`` — uplink reads method annotations eagerly.

Example:
    >>> from ycli.yandex.wiki.pages.client import PagesClient
    >>> PagesClient.from_env()  # doctest: +SKIP
"""

import requests
import uplink
from typing import ClassVar, Self

from ycli.yandex.settings import AppConfig, Credentials
from ycli.yandex.transport import Transport


class FromEnvSession:
    """Mixin: ``from_env()`` builds an authed session from the environment and injects it.

    Inherited by ``BaseYandex`` and the three composition-root clients; each defines its
    own ``__init__(*, session)``, so ``cls(session=...)`` constructs correctly. Credentials
    are validated by pydantic — a missing var raises ``pydantic.ValidationError`` here.
    """

    @classmethod
    def from_env(cls) -> Self:
        credentials = Credentials()
        config = AppConfig()
        session = Transport.session(
            oauth_token=credentials.oauth_token,
            organization_id=credentials.organization_id,
            timeout_seconds=config.timeout_seconds,
            retries=config.retries,
        )
        return cls(session=session)


class BaseYandex(FromEnvSession, uplink.Consumer):
    """Required-``session`` DI + ``from_env`` (via mixin) + ``base_url`` classvar."""

    base_url: ClassVar[str]

    def __init__(self, *, session: requests.Session) -> None:
        base = self.base_url.rstrip("/") + "/"
        self._session: requests.Session = session
        super().__init__(base_url=base, client=session)
