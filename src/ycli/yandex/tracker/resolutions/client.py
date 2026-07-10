"""Declarative Tracker resolutions client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.resolutions.models import (
    Resolution,
    ResolutionCreate,
    ResolutionList,
    ResolutionUpdate,
)


class ResolutionsClient(TrackerResource):
    """Declarative HTTP for ``/resolutions`` (list + create + edit)."""

    @uplink.returns.json()
    @uplink.get("resolutions")
    def list(self) -> ResolutionList:  # ty: ignore[empty-body]
        """``GET /resolutions`` → resolution listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.resolutions.list().root[0].key  # doctest: +SKIP
            'fixed'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("resolutions/")
    def _create(self, body: uplink.Body) -> Resolution:  # ty: ignore[empty-body]
        """``POST /resolutions/`` — create from a ready JSON body (see ``create``)."""

    def create(self, body: ResolutionCreate) -> Resolution:
        """Create a resolution from a typed ``ResolutionCreate`` body. Returns the ``Resolution``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.resolutions.create(
            ...     ResolutionCreate(key="wontFix", name=LocalizedName(ru="Отклонено"))
            ... ).key  # doctest: +SKIP
            'wontFix'
        """
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("resolutions/{resolution_id}")
    def _edit(
        self,
        resolution_id: uplink.Path,
        body: uplink.Body,
        version: uplink.Query("version") = None,  # ty: ignore[invalid-type-form]
    ) -> Resolution:  # ty: ignore[empty-body]
        """``PATCH /resolutions/{resolution_id}?version=`` — edit (see ``edit``)."""

    def edit(
        self, resolution_id: str, body: ResolutionUpdate, *, version: int | None = None
    ) -> Resolution:
        """Edit resolution ``resolution_id`` from a typed ``ResolutionUpdate`` body.

        ``version`` is the current resolution version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version with 409).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.resolutions.edit(
            ...     "9", ResolutionUpdate(description="Won't be fixed"), version=1
            ... ).id  # doctest: +SKIP
            9
        """
        return self._edit(
            resolution_id=resolution_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
            version=version,
        )
