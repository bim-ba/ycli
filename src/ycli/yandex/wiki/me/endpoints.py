"""Wiki ``/users/me``, declared once (sans-IO).

Examples:
    >>> get().path
    'users/me'
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.wiki.me.models import Me


def get() -> Endpoint[Me]:
    return Endpoint(HTTPMethod.GET, "users/me", Me)
