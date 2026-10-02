"""Tracker ``/myself``, declared once (sans-IO).

Examples:
    >>> get_me().path
    'myself'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.tracker.me.models import Me


def get_me() -> Endpoint[Me]:
    return Endpoint("GET", "myself", Me)
