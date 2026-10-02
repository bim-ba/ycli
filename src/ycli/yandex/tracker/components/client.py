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
        ComponentGroupAccess,
        ComponentList,
        ComponentUpdate,
        ComponentUserAccess,
    )


class ComponentsClient(Resource):
    """List, get, create, edit and delete queue components; read who may use them."""

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

    def list_for_queue(self, queue_id: str, *, fields: str | None = None) -> ComponentList:
        """``GET /queues/{queue_id}/components`` → the components of one queue.

        ``fields`` is a comma list of extra fields (``version,description,lead,assignAuto``);
        ``self``, ``id``, ``name`` and ``queue`` always come back.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.list_for_queue("TEST").root[0].name  # doctest: +SKIP
            'UI'
        """
        return self._session.send(endpoints.list_queue_components(queue_id, fields=fields))

    def get(self, component_id: int, *, fields: str | None = None) -> Component:
        """``GET /components/{component_id}`` → one component.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.get(111175, fields="name,lead").name  # doctest: +SKIP
            'UI'
        """
        return self._session.send(endpoints.get_component(component_id, fields=fields))

    def delete(self, component_id: int) -> None:
        """``DELETE /components/{component_id}`` → 204; raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.delete(111175)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_component(component_id))

    def user_permissions(self, component_id: int, user_id: str) -> ComponentUserAccess:
        """``GET /components/{id}/permissions/users/{user_id}`` → a user's rights on a component.

        ``user_id`` is a login or a numeric uid.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.user_permissions(1, "alice").permissions.read  # doctest: +SKIP
        """
        return self._session.send(endpoints.get_user_access(component_id, user_id))

    def group_permissions(self, component_id: int, group_id: int) -> ComponentGroupAccess:
        """``GET /components/{id}/permissions/groups/{group_id}`` → a group's rights on it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.components.group_permissions(1, 5).permissions.read  # doctest: +SKIP
        """
        return self._session.send(endpoints.get_group_access(component_id, group_id))
