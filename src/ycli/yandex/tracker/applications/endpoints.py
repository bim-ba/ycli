"""Tracker ``/applications``, declared once (sans-IO).

Examples:
    >>> list_applications().path
    'applications'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.tracker.applications.models import ApplicationList


def list_applications() -> Endpoint[ApplicationList]:
    return Endpoint("GET", "applications", ApplicationList)
