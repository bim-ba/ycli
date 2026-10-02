"""Tracker ``/linktypes``, declared once (sans-IO).

Example:
    >>> list_link_types().path
    'linktypes'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.tracker.linktypes.models import LinkTypeList


def list_link_types() -> Endpoint[LinkTypeList]:
    return Endpoint("GET", "linktypes", LinkTypeList)
