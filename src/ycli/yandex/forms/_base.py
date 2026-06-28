"""Per-domain base — carries the Forms API base_url; resource clients inherit it.

Forms lives on its OWN host (``api.forms.yandex.net``), distinct from Tracker/Wiki —
this base is the single place that fact is encoded.

NOTE: no ``from __future__ import annotations`` — resource clients subclass this and
uplink reads their method annotations eagerly. Keep this module annotation-eager too.
"""
from typing import ClassVar

from ycli.yandex.base import BaseYandex


class FormsResource(BaseYandex):
    """Base for every Forms resource client (inherits session DI via constructor)."""

    base_url: ClassVar[str] = "https://api.forms.yandex.net/v1"
