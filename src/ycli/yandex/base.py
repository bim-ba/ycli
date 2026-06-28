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

import requests
import uplink
from typing import ClassVar


class BaseYandex(uplink.Consumer):
    """Required-``session`` DI + ``base_url`` classvar."""

    base_url: ClassVar[str]

    def __init__(self, *, session: requests.Session) -> None:
        base = self.base_url.rstrip("/") + "/"
        self._session: requests.Session = session
        super().__init__(base_url=base, client=session)
