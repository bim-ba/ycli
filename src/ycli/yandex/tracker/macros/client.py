"""Tracker queue ``/macros`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.macros import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.macros.models import Macro, MacroCreate, MacroList, MacroUpdate


class MacrosClient(Resource):
    """List, get, create, edit and delete a queue's macros."""

    def list(self, queue_id: str) -> MacroList:
        """``GET /queues/{queue_id}/macros`` → the queue's macros.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.list(queue_id="TEST").root[0].name  # doctest: +SKIP
            'My macro'
        """
        return self._session.send(endpoints.list_macros(queue_id))

    def get(self, queue_id: str, macro_id: int) -> Macro:
        """``GET /queues/{queue_id}/macros/{macro_id}`` → a single macro.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.get(queue_id="TEST", macro_id=3).name  # doctest: +SKIP
            'My macro'
        """
        return self._session.send(endpoints.get_macro(queue_id, macro_id))

    def create(self, queue_id: str, body: MacroCreate) -> Macro:
        """Create a macro from a typed ``MacroCreate`` body. Returns the created ``Macro``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.create("TEST", MacroCreate(name="Test macro")).id  # doctest: +SKIP
            3
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_macro(queue_id, dumped))

    def edit(self, queue_id: str, macro_id: int, body: MacroUpdate) -> Macro:
        """Edit a macro from a typed ``MacroUpdate`` body. Returns the updated ``Macro``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.edit("TEST", 3, MacroUpdate(name="Renamed")).name  # doctest: +SKIP
            'Renamed'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_macro(queue_id, macro_id, dumped))

    def delete(self, queue_id: str, macro_id: int) -> None:
        """``DELETE /queues/{queue_id}/macros/{macro_id}`` — delete a macro (``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.delete("TEST", 3)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_macro(queue_id, macro_id))
