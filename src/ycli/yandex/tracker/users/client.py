"""Declarative Tracker users client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.users.models import User, UserList, UsersRelativeResponse


class UsersClient(TrackerResource):
    """Declarative HTTP for ``/users`` (get + relative-paginated list)."""

    @uplink.returns.json()
    @uplink.get("users/{login_or_id}")
    def get(
        self,
        login_or_id: uplink.Path,
        expand: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> User:  # ty: ignore[empty-body]
        """``GET /users/{login_or_id}`` → one user account.

        ``expand=groups`` adds the user's groups. For a numeric login use ``login:<digits>``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.users.get(login_or_id="username").display  # doctest: +SKIP
            'Ivan Ivanov'
        """

    @uplink.returns.json()
    @uplink.get("users/_relative")
    def _relative_page(
        self,
        per_page: uplink.Query("perPage") = 100,  # ty: ignore[invalid-type-form]
        user_id: uplink.Query("id") = None,  # ty: ignore[invalid-type-form]
        expand: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> UsersRelativeResponse:  # ty: ignore[empty-body]
        """One raw ``/users/_relative`` page (``{users, hasNext}``); callers use ``list``."""

    def list(self, *, limit: int | None = None, expand: str | None = None) -> UserList:
        """All organisation users, draining the ``id=<last uid>`` relative cursor internally.

        Users come back sorted by ascending ``uid``; each next page repeats with
        ``id=<uid of the last user seen>``. Capped at ``limit`` (``None`` = every user).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.users.list(limit=50).root[0].login  # doctest: +SKIP
            'username'
        """
        users = self._drain_relative(
            extract=lambda page: page.users,
            id_of=lambda user: str(user.uid) if user.uid is not None else None,
            fetch_page=lambda cursor, per_page: self._relative_page(
                per_page=per_page, user_id=cursor, expand=expand
            ),
            limit=limit,
        )
        return UserList(users)
