"""Declarative Tracker issue-checklists client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.

The ``get`` read returns a bare array of items (``ChecklistItemList``); every write
(create/edit/delete-item/clear) returns the issue wrapper with the updated
``checklistItems`` embedded (``Checklist``) — including the delete calls, which the API
answers with ``200 OK`` and a body (not ``204``).
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.checklists.models import Checklist, ChecklistItemList


class ChecklistsClient(TrackerResource):
    """Declarative HTTP for ``/issues/{key}/checklistItems``."""

    @uplink.returns.json()
    @uplink.get("issues/{key}/checklistItems")
    def get(self, key: uplink.Path) -> ChecklistItemList:  # ty: ignore[empty-body]
        """``GET /issues/{key}/checklistItems`` → the issue's checklist items.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.get(key="DATAENGINEERING-1").root[0].text  # doctest: +SKIP
            'Review the PR'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{key}/checklistItems")
    def create(self, key: uplink.Path, body: uplink.Body) -> Checklist:  # ty: ignore[empty-body]
        """``POST /issues/{key}/checklistItems`` — add an item. Returns the issue wrapper.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.create(
            ...     "DATAENGINEERING-1", {"text": "step 1"}
            ... ).key  # doctest: +SKIP
            'DATAENGINEERING-1'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("issues/{key}/checklistItems/{item_id}")
    def edit(self, key: uplink.Path, item_id: uplink.Path, body: uplink.Body) -> Checklist:  # ty: ignore[empty-body]
        """``PATCH /issues/{key}/checklistItems/{item_id}`` — edit an item. Returns the wrapper.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.edit(
            ...     "DATAENGINEERING-1", "5f", {"checked": True}
            ... ).key  # doctest: +SKIP
            'DATAENGINEERING-1'
        """

    @uplink.returns.json()
    @uplink.delete("issues/{key}/checklistItems/{item_id}")
    def delete(self, key: uplink.Path, item_id: uplink.Path) -> Checklist:  # ty: ignore[empty-body]
        """``DELETE /issues/{key}/checklistItems/{item_id}`` — remove one item (200 + wrapper).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.delete(
            ...     "DATAENGINEERING-1", "5f"
            ... ).checklist_total  # doctest: +SKIP
            3
        """

    @uplink.returns.json()
    @uplink.delete("issues/{key}/checklistItems")
    def clear(self, key: uplink.Path) -> Checklist:  # ty: ignore[empty-body]
        """``DELETE /issues/{key}/checklistItems`` — remove the whole checklist (200 + wrapper).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.clear("DATAENGINEERING-1").checklist_items  # doctest: +SKIP
            []
        """
