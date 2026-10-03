"""Tracker ``/applications``, declared once (sans-IO).

Examples:
    >>> list_applications().path
    'applications'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.applications.models import Application


def list_applications() -> Endpoint[ItemList[Application]]:
    return Endpoint("GET", "applications", ItemList[Application])
