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

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.statuses.list().root[0].key  # doctest: +SKIP
            'open'
        """
        return self._session.send(endpoints.list_statuses())

    def create(self, body: StatusCreate) -> Status:
        """Create an issue status from a typed ``StatusCreate`` body. Returns the new ``Status``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.statuses.create(
            ...     StatusCreate(key="pause", name=LocalizedName(ru="Пауза"), type="paused")
            ... ).key  # doctest: +SKIP
            'pause'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_status(dumped))

    def edit(self, status_id: str, body: StatusUpdate, *, version: int | None = None) -> Status:
        """Edit status ``status_id`` from a typed ``StatusUpdate`` body. Returns the ``Status``.

        ``version`` is the current status version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version with 409).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.statuses.edit(
            ...     "29", StatusUpdate(description="Issue is paused"), version=1
            ... ).id  # doctest: +SKIP
            29
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_status(status_id, dumped, version=version))
