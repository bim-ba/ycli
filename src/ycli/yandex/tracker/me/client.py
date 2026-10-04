"""Tracker ``/myself`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.me import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.me.models import Me


class MeClient(Resource):
    """The authenticated Tracker user."""

    def get(self) -> Me:
        """``GET /myself`` → the authenticated ``Me`` (a safe auth probe).

        Returns:
            The authenticated user.

        Examples:
            >>> tracker.me.get().login
            'alice'
        """
        return self._session.send(endpoints.get())
