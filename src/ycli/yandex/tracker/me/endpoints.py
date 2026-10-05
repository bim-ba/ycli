"""Tracker ``/myself``, declared once (sans-IO).

Examples:
    >>> get().path
    'myself'
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.tracker.me.models import Me


def get() -> Endpoint[Me]:
    return Endpoint(HTTPMethod.GET, "myself", Me)
