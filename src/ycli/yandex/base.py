"""Shared base for every Yandex resource client (uplink.Consumer).

Holds the two things every resource repeats: a required-``session`` constructor (DI —
the client takes a configured ``requests.Session``, never reaches into the env) and a
``from_env()`` classmethod. The per-API base URL is a ``base_url`` ClassVar set by a
per-domain base (e.g. ``WikiResource``); resource clients inherit it.

uplink's ``ConsumerMeta`` collects decorated request methods from the leaf subclass, so
an intermediate base with no decorated methods is fine.

NOTE: no ``from __future__ import annotations`` — uplink reads method annotations eagerly.

Example:
    >>> from ycli.yandex.wiki.pages.client import PagesClient
    >>> PagesClient.from_env()  # doctest: +SKIP
"""

import os
from typing import ClassVar, Self

import requests
import uplink

from ycli.yandex.transport import Transport


def session_from_env() -> requests.Session:
    """Build an authed session from ``$YANDEX_ID_OAUTH_TOKEN`` / ``$YANDEX_ID_ORGANIZATION_ID``.

    Raises ``ValueError`` (naming the missing variable) when either is absent/empty.
    Credential resolution lives here, NOT in ``Transport`` (which stays env-free).

    Example:
        >>> session_from_env()  # doctest: +SKIP
    """
    token = os.environ.get("YANDEX_ID_OAUTH_TOKEN", "")
    org_id = os.environ.get("YANDEX_ID_ORGANIZATION_ID", "")
    if not token:
        raise ValueError("YANDEX_ID_OAUTH_TOKEN is empty — set it in the environment")
    if not org_id:
        raise ValueError("YANDEX_ID_ORGANIZATION_ID is empty — set it in the environment")
    return Transport.session(token=token, org_id=org_id)


class BaseYandex(uplink.Consumer):
    """Required-``session`` DI + ``from_env`` env resolution + ``base_url`` classvar."""

    base_url: ClassVar[str]

    def __init__(self, *, session: requests.Session) -> None:
        # uplink joins paths with urljoin; a base without a trailing slash drops the
        # last segment (".../v1" + "pages" -> ".../pages"). Normalize so a base_url
        # with no trailing slash is safe.
        base = self.base_url.rstrip("/") + "/"
        # Retain the raw requests.Session before super().__init__ wraps it — uplink's
        # own ``self.session`` is a wrapper that does not expose the injected headers.
        self._session: requests.Session = session
        super().__init__(base_url=base, client=session)

    @classmethod
    def from_env(cls) -> Self:
        """Build a client from ``$YANDEX_ID_*`` (raises on a missing var).

        Example:
            >>> BaseYandex.from_env()  # doctest: +SKIP
        """
        return cls(session=session_from_env())
