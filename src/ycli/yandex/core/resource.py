"""``Resource`` — the base of every resource client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.yandex.core.session import SyncSession


class Resource:
    """Holds the session a resource client sends its endpoints through.

    Args:
        session: The session the resource's endpoints are sent through.

    Examples:
        >>> from http import HTTPMethod
        >>> from ycli.yandex.core.endpoint import Endpoint
        >>> from ycli.yandex.tracker.me.models import Me
        >>> class MeClient(Resource):
        ...     def get(self) -> Me:
        ...         return self._session.send(Endpoint(HTTPMethod.GET, "myself", Me))
        >>> MeClient(session=tracker.me._session).get().login
        'alice'
    """

    def __init__(self, *, session: SyncSession) -> None:
        self._session = session
