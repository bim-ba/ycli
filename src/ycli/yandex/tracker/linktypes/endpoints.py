"""Tracker ``/linktypes``, declared once (sans-IO).

Examples:
    >>> list_().path
    'linktypes'
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.models import LinkType


def list_() -> Endpoint[ItemList[LinkType]]:
    return Endpoint(HTTPMethod.GET, "linktypes", ItemList[LinkType])
