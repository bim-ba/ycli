"""Tracker priorities client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.priorities.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.priorities import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.priorities.models import Priority, PriorityCreate, PriorityUpdate


class PrioritiesClient(Resource):
    """List, create and update issue priorities."""

    def list(
        self,
        *,
        localized: bool | None = None,
    ) -> ItemList[Priority]:
        """``GET /priorities`` → priority listing.

        Args:
            localized: ``False`` returns the names in every language; the API's default is the
                caller's language only.

        Returns:
            The priorities.

        Examples:
            >>> tracker.priorities.list().root[0].key
            'normal'
        """
        return self._session.send(endpoints.list_priorities(localized=localized))

    def create(self, body: PriorityCreate) -> Priority:
        """Create a priority from a typed ``PriorityCreate`` body. Returns the new ``Priority``.

        Args:
            body: The new priority's key, localized name and order.

        Returns:
            The created priority.

        Examples:
            >>> from ycli.yandex.tracker.models import LocalizedName
            >>> from ycli.yandex.tracker.priorities.models import PriorityCreate
            >>> tracker.priorities.create(
            ...     PriorityCreate(key="one", name=LocalizedName(ru="Низкий", en="Low"), order=60)
            ... ).key
            'one'
        """
        return self._session.send(endpoints.create_priority(body))

    def update(
        self, priority_id: str, body: PriorityUpdate, *, version: int | None = None
    ) -> Priority:
        """Edit priority ``priority_id`` from a typed ``PriorityUpdate`` body.

        ``version`` is the current priority version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version with 409).

        Args:
            priority_id: The priority's key or id.
            body: The fields to change.
            version: The current priority version, sent as ``?version=``; ``None`` sends none.

        Returns:
            The updated priority.

        Examples:
            >>> from ycli.yandex.tracker.priorities.models import PriorityUpdate
            >>> tracker.priorities.update(
            ...     "blocker", PriorityUpdate(description="Stops all"), version=7
            ... ).key
            'blocker'
        """
        return self._session.send(endpoints.update_priority(priority_id, body, version=version))
