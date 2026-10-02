"""Tracker saved ``/filters`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.filters import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.filters.models import Filter, FilterCreate, FilterUpdate


class FiltersClient(Resource):
    """Get, create and edit saved issue filters."""

    def get(self, filter_id: str) -> Filter:
        """``GET /filters/{filter_id}`` → parameters of one saved filter.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filters.get(filter_id="12345").name  # doctest: +SKIP
            'My open issues'
        """
        return self._session.send(endpoints.get_filter(filter_id))

    def create(self, body: FilterCreate) -> Filter:
        """Create a saved filter from a typed ``FilterCreate`` body. Returns the ``Filter``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filters.create(
            ...     FilterCreate(name="My open", filter={"status": "open"})
            ... ).id  # doctest: +SKIP
            12345
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_filter(dumped))

    def edit(self, filter_id: str, body: FilterUpdate) -> Filter:
        """Edit filter ``filter_id`` from a typed ``FilterUpdate`` body. Returns the ``Filter``.

        This endpoint has no ``?version=`` optimistic lock; the ``filter`` object is replaced
        wholesale rather than merged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filters.edit("12345", FilterUpdate(name="Renamed")).name  # doctest: +SKIP
            'Renamed'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_filter(filter_id, dumped))
