"""Declarative Tracker filters client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.filters.models import Filter, FilterCreate, FilterUpdate


class FiltersClient(TrackerResource):
    """Declarative HTTP for ``/filters`` (get + create + edit)."""

    @uplink.returns.json()
    @uplink.get("filters/{filter_id}")
    def get(self, filter_id: uplink.Path) -> Filter:  # ty: ignore[empty-body]
        """``GET /filters/{filter_id}`` → parameters of one saved filter.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filters.get(filter_id="12345").name  # doctest: +SKIP
            'My open issues'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("filters/")
    def _create(self, body: uplink.Body) -> Filter:  # ty: ignore[empty-body]
        """``POST /filters/`` — create from a ready JSON body (see ``create``)."""

    def create(self, body: FilterCreate) -> Filter:
        """Create a saved filter from a typed ``FilterCreate`` body. Returns the ``Filter``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filters.create(
            ...     FilterCreate(name="My open", filter={"status": "open"})
            ... ).id  # doctest: +SKIP
            12345
        """
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("filters/{filter_id}")
    def _edit(self, filter_id: uplink.Path, body: uplink.Body) -> Filter:  # ty: ignore[empty-body]
        """``PATCH /filters/{filter_id}`` — edit from a ready JSON body (see ``edit``)."""

    def edit(self, filter_id: str, body: FilterUpdate) -> Filter:
        """Edit filter ``filter_id`` from a typed ``FilterUpdate`` body. Returns the ``Filter``.

        This endpoint has no ``?version=`` optimistic lock; the ``filter`` object is replaced
        wholesale rather than merged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.filters.edit("12345", FilterUpdate(name="Renamed")).name  # doctest: +SKIP
            'Renamed'
        """
        return self._edit(
            filter_id=filter_id, body=body.model_dump(by_alias=True, exclude_none=True)
        )
