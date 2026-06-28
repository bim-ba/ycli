"""Per-domain base — carries the Tracker API base_url; resource clients inherit it.

NOTE: no ``from __future__ import annotations`` — resource clients subclass this and
uplink reads their method annotations eagerly. Keep this module annotation-eager too.
"""

from typing import ClassVar

from ycli.yandex.base import BaseYandex


class TrackerResource(BaseYandex):
    """Base for every Tracker resource client (inherits session DI via constructor)."""

    base_url: ClassVar[str] = "https://api.tracker.yandex.net/v3"
