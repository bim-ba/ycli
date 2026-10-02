"""Tracker saved ``/filters`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.filters import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.filters.models import Filter, FilterCreate, FilterUpdate


class FiltersClient(Resource):
    """Get, create, edit and delete saved issue filters."""

    def get(self, filter_id: str) -> Filter:
        """``GET /filters/{filter_id}`` → parameters of one saved filter.

        Args:
            filter_id: The filter's id.

        Returns:
            The saved filter.

        Examples:
            >>> tracker.filters.get("12345").name
            'My open issues'
        """
        return self._session.send(endpoints.get_filter(filter_id))

    def create(self, body: FilterCreate) -> Filter:
        """Create a saved filter from a typed ``FilterCreate`` body. Returns the ``Filter``.

        Args:
            body: The new filter's name, query and filter object.

        Returns:
            The created filter.

        Examples:
            >>> from ycli.yandex.tracker.filters.models import FilterCreate
            >>> tracker.filters.create(FilterCreate(name="My open", filter={"status": "open"})).id
            12346
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_filter(dumped))

    def edit(self, filter_id: str, body: FilterUpdate) -> Filter:
        """Edit filter ``filter_id`` from a typed ``FilterUpdate`` body. Returns the ``Filter``.

        This endpoint has no ``?version=`` optimistic lock; the ``filter`` object is replaced
        wholesale rather than merged.

        Args:
            filter_id: The filter's id.
            body: The fields to change.

        Returns:
            The updated filter.

        Examples:
            >>> from ycli.yandex.tracker.filters.models import FilterUpdate
            >>> tracker.filters.edit("12347", FilterUpdate(name="Renamed")).name
            'Renamed'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_filter(filter_id, dumped))

    def delete(self, filter_id: str) -> None:
        """``DELETE /filters/{filter_id}`` → 204; raises on non-2xx.

        The docs name the ``/v2/filters/{id}`` route; the ``/v3/`` one used by every other
        filter call deletes it too.

        Args:
            filter_id: The filter's id.

        Examples:
            >>> tracker.filters.delete("12349")
        """
        self._session.send(endpoints.delete_filter(filter_id))
