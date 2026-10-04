"""Tracker ``/components`` client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.components.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.components import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.components.models import (
        Component,
        ComponentCreate,
        ComponentGroupAccess,
        ComponentUpdate,
        ComponentUserAccess,
    )


class ComponentsClient(Resource):
    """List, get, create, update and delete queue components; read who may use them."""

    def list(self) -> ItemList[Component]:
        """``GET /components`` → all components created by the organisation's users.

        Returns:
            The components.

        Examples:
            >>> tracker.components.list().root[0].name
            'Backend'
        """
        return self._session.send(endpoints.list_())

    def create(self, body: ComponentCreate) -> Component:
        """Create a component from a typed ``ComponentCreate`` body. Returns the ``Component``.

        Args:
            body: The new component's settings.

        Returns:
            The created component.

        Examples:
            >>> from ycli.yandex.tracker.components.models import ComponentCreate
            >>> tracker.components.create(ComponentCreate(name="UI", queue="WEB")).id
            111175
        """
        return self._session.send(endpoints.create(body))

    def update(
        self, component_id: int, body: ComponentUpdate, *, version: int | None = None
    ) -> Component:
        """Edit component ``component_id`` from a typed ``ComponentUpdate`` body.

        ``version`` is the current component version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version with 409).

        Args:
            component_id: The component's id.
            body: The fields to change.
            version: The component's current version, for optimistic locking.

        Returns:
            The updated component.

        Examples:
            >>> from ycli.yandex.tracker.components.models import ComponentUpdate
            >>> tracker.components.update(111175, ComponentUpdate(name="Web UI"), version=4).version
            5
        """
        return self._session.send(endpoints.update(component_id, body, version=version))

    def list_for_queue(self, queue_id: str, *, fields: str | None = None) -> ItemList[Component]:
        """``GET /queues/{queue_id}/components`` → the components of one queue.

        ``fields`` is a comma list of extra fields (``version,description,lead,assignAuto``);
        ``self``, ``id``, ``name`` and ``queue`` always come back.

        Args:
            queue_id: The queue's key or id.
            fields: The extra fields to include, comma-separated.

        Returns:
            The queue's components.

        Examples:
            >>> tracker.components.list_for_queue("COMPQ", fields="version,description").root[
            ...     0
            ... ].name
            'Frontend'
        """
        return self._session.send(endpoints.list_for_queue(queue_id, fields=fields))

    def get(self, component_id: int, *, fields: str | None = None) -> Component:
        """``GET /components/{component_id}`` → one component.

        Args:
            component_id: The component's id.
            fields: The extra fields to include, comma-separated.

        Returns:
            The component.

        Examples:
            >>> tracker.components.get(125, fields="name,lead,assignAuto").name
            'Backend'
        """
        return self._session.send(endpoints.get(component_id, fields=fields))

    def delete(self, component_id: int) -> None:
        """``DELETE /components/{component_id}`` → 204; raises on non-2xx.

        Args:
            component_id: The component's id.

        Examples:
            >>> tracker.components.delete(127)
        """
        self._session.send(endpoints.delete(component_id))

    def user_permissions_get(self, component_id: int, user_id: str) -> ComponentUserAccess:
        """``GET /components/{id}/permissions/users/{user_id}`` → a user's rights on a component.

        ``user_id`` is a login or a numeric uid.

        Args:
            component_id: The component's id.
            user_id: The user's login or numeric uid.

        Returns:
            The user's rights on the component.

        Examples:
            >>> tracker.components.user_permissions_get(128, "dan").user.display
            'Dan'
        """
        return self._session.send(endpoints.user_permissions_get(component_id, user_id))

    def group_permissions_get(self, component_id: int, group_id: int) -> ComponentGroupAccess:
        """``GET /components/{id}/permissions/groups/{group_id}`` → a group's rights on it.

        Args:
            component_id: The component's id.
            group_id: The group's id.

        Returns:
            The group's rights on the component.

        Examples:
            >>> tracker.components.group_permissions_get(129, 88).group.display
            'Reviewers'
        """
        return self._session.send(endpoints.group_permissions_get(component_id, group_id))
