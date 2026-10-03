"""Tracker priorities client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.priorities.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.priorities import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.priorities.models import (
        Priority,
        PriorityCreate,
        PriorityList,
        PriorityUpdate,
    )


class PrioritiesClient(Resource):
    """List, create and edit issue priorities."""

    def list(self) -> PriorityList:
        """``GET /priorities`` → priority listing.

        Returns:
            The priorities.

        Examples:
            >>> tracker.priorities.list().root[0].key
            'normal'
        """
        return self._session.send(endpoints.list_priorities())

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
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_priority(dumped))

    def edit(
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
            >>> tracker.priorities.edit(
            ...     "blocker", PriorityUpdate(description="Stops all"), version=7
            ... ).key
            'blocker'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_priority(priority_id, dumped, version=version))
