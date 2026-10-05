"""Forms ``/users/me``, declared once (sans-IO).

Examples:
    >>> get().path
    'users/me'
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.forms.me.models import User


def get() -> Endpoint[User]:
    return Endpoint(HTTPMethod.GET, "users/me", User)
