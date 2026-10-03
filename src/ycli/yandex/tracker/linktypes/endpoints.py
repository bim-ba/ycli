"""Tracker ``/linktypes``, declared once (sans-IO).

Examples:
    >>> list_link_types().path
    'linktypes'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.models import LinkType


def list_link_types() -> Endpoint[ItemList[LinkType]]:
    return Endpoint("GET", "linktypes", ItemList[LinkType])
