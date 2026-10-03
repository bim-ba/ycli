"""Tracker issue ``/checklistItems`` client on the httpx2 core.

The ``get`` read returns a bare array of items (``ItemList[ChecklistItem]``); every write
(create/edit/delete-item/clear) returns the issue wrapper with the updated
``checklistItems`` embedded (``Checklist``) — including the delete calls, which the API
answers with ``200 OK`` and a body (not ``204``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.checklists import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.checklists.models import Checklist, ChecklistItem


class ChecklistsClient(Resource):
    """Get, add, edit and delete an issue's checklist items, or clear the whole checklist."""

    def get(self, key: str) -> ItemList[ChecklistItem]:
        """``GET /issues/{key}/checklistItems`` → the issue's checklist items.

        Args:
            key: The issue key.

        Returns:
            The issue's checklist items.

        Examples:
            >>> tracker.checklists.get("DE-31").root[0].text
            'Review the PR'
        """
        return self._session.send(endpoints.get_checklist(key))

    def create(self, key: str, body: dict[str, Any]) -> Checklist:
        """``POST /issues/{key}/checklistItems`` — add an item. Returns the issue wrapper.

        Args:
            key: The issue key.
            body: The new item: its text and optional checked flag, assignee and deadline.

        Returns:
            The issue wrapper with the updated checklist.

        Examples:
            >>> tracker.checklists.create("DE-32", {"text": "step 1"}).key
            'DE-32'
        """
        return self._session.send(endpoints.create_checklist_item(key, body))

    def edit(self, key: str, item_id: str, body: dict[str, Any]) -> Checklist:
        """``PATCH /issues/{key}/checklistItems/{item_id}`` — edit an item. Returns the wrapper.

        Args:
            key: The issue key.
            item_id: The checklist item's id.
            body: The item fields to change.

        Returns:
            The issue wrapper with the updated checklist.

        Examples:
            >>> tracker.checklists.edit("DE-34", "5f4", {"text": "step 2"}).key
            'DE-34'
        """
        return self._session.send(endpoints.edit_checklist_item(key, item_id, body))

    def delete(self, key: str, item_id: str) -> Checklist:
        """``DELETE /issues/{key}/checklistItems/{item_id}`` — remove one item (200 + wrapper).

        Args:
            key: The issue key.
            item_id: The checklist item's id.

        Returns:
            The issue wrapper with the remaining checklist.

        Examples:
            >>> tracker.checklists.delete("DE-36", "5f6").checklist_items[0].text
            'left'
        """
        return self._session.send(endpoints.delete_checklist_item(key, item_id))

    def clear(self, key: str) -> Checklist:
        """``DELETE /issues/{key}/checklistItems`` — remove the whole checklist (200 + wrapper).

        Args:
            key: The issue key.

        Returns:
            The issue wrapper with an empty checklist.

        Examples:
            >>> tracker.checklists.clear("DE-37").checklist_items
            []
        """
        return self._session.send(endpoints.clear_checklist(key))
