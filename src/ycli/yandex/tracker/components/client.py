"""Tracker ``/components`` client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.components.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.components import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.components.models import (
        Component,
        ComponentCreate,
        ComponentList,
        ComponentUpdate,
    )


class ComponentsClient(Resource):
    """List, create and edit queue components."""

    def list(self) -> ComponentList:
        """``GET /components`` → all components created by the organisation's users.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.list().root[0].name  # doctest: +SKIP
            'Test'
        """
        return self._session.send(endpoints.list_components())

    def create(self, body: ComponentCreate) -> Component:
        """Create a component from a typed ``ComponentCreate`` body. Returns the ``Component``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.create(
            ...     ComponentCreate(name="UI", queue="TEST")
            ... ).id  # doctest: +SKIP
            111175
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_component(dumped))

    def edit(
        self, component_id: int, body: ComponentUpdate, *, version: int | None = None
    ) -> Component:
        """Edit component ``component_id`` from a typed ``ComponentUpdate`` body.

        ``version`` is the current component version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version with 409).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.edit(
            ...     111175, ComponentUpdate(assign_auto=True), version=1
            ... ).assign_auto  # doctest: +SKIP
            True
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_component(component_id, dumped, version=version))
