"""Declarative Tracker statuses client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.statuses.models import Status, StatusCreate, StatusList, StatusUpdate


class StatusesClient(TrackerResource):
    """Declarative HTTP for ``/statuses`` (list + create + edit)."""

    @uplink.returns.json()
    @uplink.get("statuses")
    def list(self) -> StatusList:  # ty: ignore[empty-body]
        """``GET /statuses`` → status listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.statuses.list().root[0].key  # doctest: +SKIP
            'open'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("statuses/")
    def _create(self, body: uplink.Body) -> Status:  # ty: ignore[empty-body]
        """``POST /statuses/`` — create from a ready JSON body (see ``create``)."""

    def create(self, body: StatusCreate) -> Status:
        """Create an issue status from a typed ``StatusCreate`` body. Returns the new ``Status``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.statuses.create(
            ...     StatusCreate(key="pause", name=LocalizedName(ru="Пауза"), type="paused")
            ... ).key  # doctest: +SKIP
            'pause'
        """
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("statuses/{status_id}")
    def _edit(
        self,
        status_id: uplink.Path,
        body: uplink.Body,
        version: uplink.Query("version") = None,  # ty: ignore[invalid-type-form]
    ) -> Status:  # ty: ignore[empty-body]
        """``PATCH /statuses/{status_id}?version=`` — edit from a ready body (see ``edit``)."""

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
        return self._edit(
            status_id=status_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
            version=version,
        )
