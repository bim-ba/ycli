"""Declarative Tracker priorities client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.priorities.models import (
    Priority,
    PriorityCreate,
    PriorityList,
    PriorityUpdate,
)


class PrioritiesClient(TrackerResource):
    """Declarative HTTP for ``/priorities`` (list + create + edit)."""

    @uplink.returns.json()
    @uplink.get("priorities")
    def list(self) -> PriorityList:  # ty: ignore[empty-body]
        """``GET /priorities`` → priority listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.priorities.list().root[0].key  # doctest: +SKIP
            'normal'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("priorities/")
    def _create(self, body: uplink.Body) -> Priority:  # ty: ignore[empty-body]
        """``POST /priorities/`` — create from a ready JSON body (see ``create``)."""

    def create(self, body: PriorityCreate) -> Priority:
        """Create a priority from a typed ``PriorityCreate`` body. Returns the new ``Priority``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.priorities.create(
            ...     PriorityCreate(key="one", name=LocalizedName(ru="Низкий"), order=60)
            ... ).key  # doctest: +SKIP
            'one'
        """
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("priorities/{priority_id}")
    def _edit(
        self,
        priority_id: uplink.Path,
        body: uplink.Body,
        version: uplink.Query("version") = None,  # ty: ignore[invalid-type-form]
    ) -> Priority:  # ty: ignore[empty-body]
        """``PATCH /priorities/{priority_id}?version=`` — edit from a ready body (see ``edit``)."""

    def edit(
        self, priority_id: str, body: PriorityUpdate, *, version: int | None = None
    ) -> Priority:
        """Edit priority ``priority_id`` from a typed ``PriorityUpdate`` body.

        ``version`` is the current priority version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version with 409).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.priorities.edit(
            ...     "one", PriorityUpdate(name=LocalizedName(ru="Низкий")), version=1
            ... ).key  # doctest: +SKIP
            'one'
        """
        return self._edit(
            priority_id=priority_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
            version=version,
        )
