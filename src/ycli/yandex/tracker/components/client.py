"""Declarative Tracker components client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.components.models import (
    Component,
    ComponentCreate,
    ComponentList,
    ComponentUpdate,
)


class ComponentsClient(TrackerResource):
    """Declarative HTTP for ``/components`` (list + create + edit)."""

    @uplink.returns.json()
    @uplink.get("components")
    def list(self) -> ComponentList:  # ty: ignore[empty-body]
        """``GET /components`` → all components created by the organisation's users.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.list().root[0].name  # doctest: +SKIP
            'Test'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("components")
    def _create(self, body: uplink.Body) -> Component:  # ty: ignore[empty-body]
        """``POST /components`` — create from a ready JSON body (see ``create``)."""

    def create(self, body: ComponentCreate) -> Component:
        """Create a component from a typed ``ComponentCreate`` body. Returns the ``Component``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.create(
            ...     ComponentCreate(name="UI", queue="TEST")
            ... ).id  # doctest: +SKIP
            111175
        """
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("components/{component_id}")
    def _edit(
        self,
        component_id: uplink.Path,
        body: uplink.Body,
        version: uplink.Query("version") = None,  # ty: ignore[invalid-type-form]
    ) -> Component:  # ty: ignore[empty-body]
        """``PATCH /components/{component_id}?version=`` — edit from a ready body (see ``edit``)."""

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
        return self._edit(
            component_id=component_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
            version=version,
        )
