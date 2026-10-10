"""Tracker ``/users`` client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.users.endpoints`.
"""

from ycli.yandex.core.listing import Listing
from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.users import endpoints
from ycli.yandex.tracker.users.models import User


class UsersClient(Resource):
    """Get one user; list every user over the relative ``id`` cursor."""

    def get(self, login_or_id: str, expand: str | None = None) -> User:
        """``GET /users/{login_or_id}`` → one user account.

        ``expand=groups`` adds the user's groups. For a numeric login use ``login:<digits>``.

        Args:
            login_or_id: The user's login or numeric id.
            expand: Extra blocks to include; ``groups`` adds the user's groups.

        Returns:
            The user.

        Examples:
            >>> tracker.users.get("username", expand="groups").display
            'Ivan Ivanov'
        """
        return self._session.send(endpoints.get(login_or_id, expand=expand))

    def list(
        self, *, limit: int | None = None, next: str | None = None, expand: str | None = None
    ) -> Listing[User]:
        """All organisation users, draining the ``id=<last uid>`` relative cursor internally.

        Users come back sorted by ascending ``uid``; each next page repeats with
        ``id=<uid of the last user seen>``. Capped at ``limit`` (``None`` = every user).

        Args:
            limit: The most users to return; ``None`` returns every user.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.
            expand: Extra blocks to include, as in :meth:`get`.

        Returns:
            The organisation's users, ascending by ``uid``.

        Examples:
            >>> [user.uid for user in tracker.users.list(limit=500, expand="groups")]
            [1, 2, 3]
        """
        # A small cap needs no full page.
        per_page = min(endpoints.MAX_PAGE_SIZE, limit) if limit else endpoints.MAX_PAGE_SIZE
        paged = endpoints.list_(per_page=per_page, expand=expand)
        return self._session.iterate(paged, limit=limit, next=next)
