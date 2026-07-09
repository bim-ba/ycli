"""Declarative Tracker queue macros client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.macros.models import Macro, MacroCreate, MacroList, MacroUpdate


class MacrosClient(TrackerResource):
    """Declarative HTTP for a queue's ``/macros`` (list, get, create, edit, delete)."""

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/macros")
    def list(self, queue_id: uplink.Path) -> MacroList:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/macros`` → the queue's macros.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.list(queue_id="TEST").root[0].name  # doctest: +SKIP
            'My macro'
        """

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/macros/{macro_id}")
    def get(self, queue_id: uplink.Path, macro_id: uplink.Path) -> Macro:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/macros/{macro_id}`` → a single macro.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.get(queue_id="TEST", macro_id=3).name  # doctest: +SKIP
            'My macro'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("queues/{queue_id}/macros")
    def _create(self, queue_id: uplink.Path, body: uplink.Body) -> Macro:  # ty: ignore[empty-body]
        """``POST /queues/{queue_id}/macros`` from a ready JSON body (see ``create``)."""

    def create(self, queue_id: str, body: MacroCreate) -> Macro:
        """Create a macro from a typed ``MacroCreate`` body. Returns the created ``Macro``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.create("TEST", MacroCreate(name="Test macro")).id  # doctest: +SKIP
            3
        """
        return self._create(
            queue_id=queue_id, body=body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("queues/{queue_id}/macros/{macro_id}")
    def _edit(self, queue_id: uplink.Path, macro_id: uplink.Path, body: uplink.Body) -> Macro:  # ty: ignore[empty-body]
        """``PATCH /queues/{queue_id}/macros/{macro_id}`` from a ready body (see ``edit``)."""

    def edit(self, queue_id: str, macro_id: int, body: MacroUpdate) -> Macro:
        """Edit a macro from a typed ``MacroUpdate`` body. Returns the updated ``Macro``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.edit("TEST", 3, MacroUpdate(name="Renamed")).name  # doctest: +SKIP
            'Renamed'
        """
        return self._edit(
            queue_id=queue_id,
            macro_id=macro_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
        )

    @uplink.delete("queues/{queue_id}/macros/{macro_id}")
    def delete(self, queue_id: uplink.Path, macro_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /queues/{queue_id}/macros/{macro_id}`` — delete a macro (``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.macros.delete("TEST", 3).status_code  # doctest: +SKIP
            204
        """
