"""Tracker issue ``/checklistItems`` client on the httpx2 core.

The ``get`` read returns a bare array of items (``ChecklistItemList``); every write
(create/edit/delete-item/clear) returns the issue wrapper with the updated
``checklistItems`` embedded (``Checklist``) — including the delete calls, which the API
answers with ``200 OK`` and a body (not ``204``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.checklists import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.checklists.models import Checklist, ChecklistItemList


class ChecklistsClient(Resource):
    """Get, add, edit and delete an issue's checklist items, or clear the whole checklist."""

    def get(self, key: str) -> ChecklistItemList:
        """``GET /issues/{key}/checklistItems`` → the issue's checklist items.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.get(key="DATAENGINEERING-1").root[0].text  # doctest: +SKIP
            'Review the PR'
        """
        return self._session.send(endpoints.get_checklist(key))

    def create(self, key: str, body: dict[str, Any]) -> Checklist:
        """``POST /issues/{key}/checklistItems`` — add an item. Returns the issue wrapper.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.create(
            ...     "DATAENGINEERING-1", {"text": "step 1"}
            ... ).key  # doctest: +SKIP
            'DATAENGINEERING-1'
        """
        return self._session.send(endpoints.create_checklist_item(key, body))

    def edit(self, key: str, item_id: str, body: dict[str, Any]) -> Checklist:
        """``PATCH /issues/{key}/checklistItems/{item_id}`` — edit an item. Returns the wrapper.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.edit(
            ...     "DATAENGINEERING-1", "5f", {"checked": True}
            ... ).key  # doctest: +SKIP
            'DATAENGINEERING-1'
        """
        return self._session.send(endpoints.edit_checklist_item(key, item_id, body))

    def delete(self, key: str, item_id: str) -> Checklist:
        """``DELETE /issues/{key}/checklistItems/{item_id}`` — remove one item (200 + wrapper).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.delete(
            ...     "DATAENGINEERING-1", "5f"
            ... ).checklist_total  # doctest: +SKIP
            3
        """
        return self._session.send(endpoints.delete_checklist_item(key, item_id))

    def clear(self, key: str) -> Checklist:
        """``DELETE /issues/{key}/checklistItems`` — remove the whole checklist (200 + wrapper).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.checklists.clear("DATAENGINEERING-1").checklist_items  # doctest: +SKIP
            []
        """
        return self._session.send(endpoints.clear_checklist(key))
