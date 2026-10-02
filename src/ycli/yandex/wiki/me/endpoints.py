"""Wiki ``/users/me``, declared once (sans-IO).

Example:
    >>> get_me().path
    'users/me'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.wiki.me.models import Me


def get_me() -> Endpoint[Me]:
    return Endpoint("GET", "users/me", Me)
