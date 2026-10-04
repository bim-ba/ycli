"""Tracker ``/users`` operations, declared once (sans-IO).

Examples:
    >>> list_users(per_page=10).endpoint.params
    {'perPage': 10, 'expand': None}
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIDPagination
from ycli.yandex.tracker.users.models import User, UsersRelativeResponse

# The largest page /users/_relative serves.
MAX_PAGE_SIZE = 100


def get_user(login_or_id: str, *, expand: str | None = None) -> Endpoint[User]:
    return Endpoint("GET", f"users/{segment(login_or_id)}", User, params={"expand": expand})


def _uid(user: User) -> str | None:
    return str(user.uid) if user.uid is not None else None


def list_users(
    *, per_page: int = MAX_PAGE_SIZE, expand: str | None = None
) -> Paged[UsersRelativeResponse, User]:
    """``GET /users/_relative``: users by ascending ``uid``.

    The next page repeats with ``id=<uid of the last user seen>``.
    """
    return Paged(
        Endpoint(
            "GET",
            "users/_relative",
            UsersRelativeResponse,
            params={"perPage": per_page, "expand": expand},
        ),
        RelativeIDPagination(id_of=_uid),
        lambda page: page.users,
    )
