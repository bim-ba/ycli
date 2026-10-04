"""Tracker ``/myself``, declared once (sans-IO).

Examples:
    >>> get().path
    'myself'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.tracker.me.models import Me


def get() -> Endpoint[Me]:
    return Endpoint("GET", "myself", Me)
