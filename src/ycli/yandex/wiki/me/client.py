"""Wiki ``/users/me`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.me import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.me.models import Me


class MeClient(Resource):
    """The authenticated Wiki user."""

    def get(self) -> Me:
        """``GET /users/me`` → the authenticated ``Me`` (a safe auth probe).

        Returns:
            The authenticated user.

        Examples:
            >>> wiki.me.get().username
            'vera.petrova'
        """
        return self._session.send(endpoints.get())
