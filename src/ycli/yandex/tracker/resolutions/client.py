"""Tracker resolutions client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.resolutions.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.resolutions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.resolutions.models import (
        Resolution,
        ResolutionCreate,
        ResolutionList,
        ResolutionUpdate,
    )


class ResolutionsClient(Resource):
    """List, create and edit issue resolutions."""

    def list(self) -> ResolutionList:
        """``GET /resolutions`` → resolution listing.

        Returns:
            The resolutions.

        Examples:
            >>> tracker.resolutions.list().root[0].key
            'fixed'
        """
        return self._session.send(endpoints.list_resolutions())

    def create(self, body: ResolutionCreate) -> Resolution:
        """Create a resolution from a typed ``ResolutionCreate`` body. Returns the ``Resolution``.

        Args:
            body: The new resolution's key and localized name.

        Returns:
            The created resolution.

        Examples:
            >>> from ycli.yandex.tracker.models import LocalizedName
            >>> from ycli.yandex.tracker.resolutions.models import ResolutionCreate
            >>> tracker.resolutions.create(
            ...     ResolutionCreate(
            ...         key="wontFix", name=LocalizedName(ru="Отклонено", en="Won't fix")
            ...     )
            ... ).key
            'wontFix'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_resolution(dumped))

    def edit(
        self, resolution_id: str, body: ResolutionUpdate, *, version: int | None = None
    ) -> Resolution:
        """Edit resolution ``resolution_id`` from a typed ``ResolutionUpdate`` body.

        ``version`` is the current resolution version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version with 409).

        Args:
            resolution_id: The resolution's key or id.
            body: The fields to change.
            version: The current resolution version, sent as ``?version=``; ``None`` sends none.

        Returns:
            The updated resolution.

        Examples:
            >>> from ycli.yandex.tracker.resolutions.models import ResolutionUpdate
            >>> tracker.resolutions.edit(
            ...     "9", ResolutionUpdate(description="Won't be fixed"), version=3
            ... ).version
            4
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_resolution(resolution_id, dumped, version=version))
