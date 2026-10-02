"""Forms ``/users/me`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.me import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.me.models import User


class MeClient(Resource):
    """The authenticated Forms user."""

    def get(self) -> User:
        """``GET /users/me`` → the authenticated ``User`` (a safe auth probe).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.me.get().email  # doctest: +SKIP
            'znatnov.s@example.com'
        """
        return self._session.send(endpoints.get_me())
