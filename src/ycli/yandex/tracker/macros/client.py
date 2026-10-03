"""Tracker queue ``/macros`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.macros import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.macros.models import Macro, MacroCreate, MacroUpdate


class MacrosClient(Resource):
    """List, get, create, edit and delete a queue's macros."""

    def list(self, queue_id: str) -> ItemList[Macro]:
        """``GET /queues/{queue_id}/macros`` → the queue's macros.

        Args:
            queue_id: The queue's key or numeric id.

        Returns:
            The queue's macros.

        Examples:
            >>> tracker.macros.list("TEST").root[0].name
            'Close'
        """
        return self._session.send(endpoints.list_macros(queue_id))

    def get(self, queue_id: str, macro_id: int) -> Macro:
        """``GET /queues/{queue_id}/macros/{macro_id}`` → a single macro.

        Args:
            queue_id: The queue's key or numeric id.
            macro_id: The macro's id.

        Returns:
            The macro.

        Examples:
            >>> tracker.macros.get("OPS", 4).name
            'Escalate'
        """
        return self._session.send(endpoints.get_macro(queue_id, macro_id))

    def create(self, queue_id: str, body: MacroCreate) -> Macro:
        """Create a macro from a typed ``MacroCreate`` body. Returns the created ``Macro``.

        Args:
            queue_id: The queue's key or numeric id.
            body: The new macro's name, comment text and issue update.

        Returns:
            The created macro.

        Examples:
            >>> from ycli.yandex.tracker.macros.models import MacroCreate
            >>> tracker.macros.create("DEV", MacroCreate(name="Triage", body="Taking a look")).id
            5
        """
        return self._session.send(endpoints.create_macro(queue_id, body))

    def edit(self, queue_id: str, macro_id: int, body: MacroUpdate) -> Macro:
        """Edit a macro from a typed ``MacroUpdate`` body. Returns the updated ``Macro``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Args:
            queue_id: The queue's key or numeric id.
            macro_id: The macro's id.
            body: The fields to change.

        Returns:
            The updated macro.

        Examples:
            >>> from ycli.yandex.tracker.macros.models import MacroUpdate
            >>> tracker.macros.edit("QA", 6, MacroUpdate(name="Renamed")).name
            'Renamed'
        """
        return self._session.send(endpoints.edit_macro(queue_id, macro_id, body))

    def delete(self, queue_id: str, macro_id: int) -> None:
        """``DELETE /queues/{queue_id}/macros/{macro_id}`` — delete a macro (``204``, empty body).

        Args:
            queue_id: The queue's key or numeric id.
            macro_id: The macro's id.

        Examples:
            >>> tracker.macros.delete("SUP", 7)
        """
        self._session.send(endpoints.delete_macro(queue_id, macro_id))
