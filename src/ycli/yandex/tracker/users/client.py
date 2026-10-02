"""Tracker ``/users`` client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.users.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.users import endpoints
from ycli.yandex.tracker.users.models import UserList

if TYPE_CHECKING:
    from ycli.yandex.tracker.users.models import User


class UsersClient(Resource):
    """Get one user; list every user over the relative ``id`` cursor."""

    def get(self, login_or_id: str, expand: str | None = None) -> User:
        """``GET /users/{login_or_id}`` → one user account.

        ``expand=groups`` adds the user's groups. For a numeric login use ``login:<digits>``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.users.get(login_or_id="username").display  # doctest: +SKIP
            'Ivan Ivanov'
        """
        return self._session.send(endpoints.get_user(login_or_id, expand=expand))

    def list(self, *, limit: int | None = None, expand: str | None = None) -> UserList:
        """All organisation users, draining the ``id=<last uid>`` relative cursor internally.

        Users come back sorted by ascending ``uid``; each next page repeats with
        ``id=<uid of the last user seen>``. Capped at ``limit`` (``None`` = every user).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.users.list(limit=50).root[0].login  # doctest: +SKIP
            'username'
        """
        # A small cap needs no full page.
        per_page = min(endpoints.MAX_PAGE_SIZE, limit) if limit else endpoints.MAX_PAGE_SIZE
        paged = endpoints.list_users(per_page=per_page, expand=expand)
        return UserList(list(self._session.iterate(paged, limit=limit)))
