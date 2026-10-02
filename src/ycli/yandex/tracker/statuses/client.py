"""Tracker statuses client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.statuses.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.statuses import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.statuses.models import Status, StatusCreate, StatusList, StatusUpdate


class StatusesClient(Resource):
    """List, create and edit issue statuses."""

    def list(self) -> StatusList:
        """``GET /statuses`` → status listing.

        Returns:
            The statuses.

        Examples:
            >>> tracker.statuses.list().root[0].key
            'open'
        """
        return self._session.send(endpoints.list_statuses())

    def create(self, body: StatusCreate) -> Status:
        """Create an issue status from a typed ``StatusCreate`` body. Returns the new ``Status``.

        Args:
            body: The new status's key, localized name and type.

        Returns:
            The created status.

        Examples:
            >>> from ycli.yandex.tracker.statuses.models import LocalizedName, StatusCreate
            >>> tracker.statuses.create(
            ...     StatusCreate(
            ...         key="pause", name=LocalizedName(ru="Пауза", en="Paused"), type="paused"
            ...     )
            ... ).key
            'pause'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_status(dumped))

    def edit(self, status_id: str, body: StatusUpdate, *, version: int | None = None) -> Status:
        """Edit status ``status_id`` from a typed ``StatusUpdate`` body. Returns the ``Status``.

        ``version`` is the current status version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version with 409).

        Args:
            status_id: The status's key or id.
            body: The fields to change.
            version: The current status version, sent as ``?version=``; ``None`` sends none.

        Returns:
            The updated status.

        Examples:
            >>> from ycli.yandex.tracker.statuses.models import StatusUpdate
            >>> tracker.statuses.edit(
            ...     "29", StatusUpdate(description="Issue is paused"), version=5
            ... ).version
            6
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_status(status_id, dumped, version=version))
