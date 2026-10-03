"""Tracker ``/queues`` client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.queues.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.queues import endpoints
from ycli.yandex.tracker.queues.models import (
    Queue,
)

if TYPE_CHECKING:
    from ycli.yandex.tracker.queues.models import (
        QueueCreate,
        QueueField,
        QueueGroupAccess,
        QueuePermissions,
        QueuePermissionsUpdate,
        QueueTagRemove,
        QueueUserAccess,
        QueueVersionCreate,
        QueueVersionInfo,
        QueueVersionUpdate,
    )


class QueuesClient(Resource):
    """List (page-paginated), get, create, delete and restore queues; tags, versions, access."""

    def list(
        self,
        *,
        limit: int | None = None,
        expand: str | None = None,
    ) -> ItemList[Queue]:
        """``GET /queues/`` → flat ``ItemList[Queue]``, draining ``page``/``perPage`` internally.

        Capped at ``limit`` (``None`` = every queue). The API returns 50 queues per page; this
        advances the page number up to ``X-Total-Pages``, or until a short page comes back.

        Args:
            limit: The most queues to return; ``None`` returns every queue.
            expand: The extra blocks to include in each queue, as in :meth:`get`.

        Returns:
            The queues, across all pages.

        Examples:
            >>> tracker.queues.list(limit=500).root[-1].key
            'TAIL'
        """
        return ItemList[Queue](
            list(self._session.iterate(endpoints.list_queues(expand=expand), limit=limit))
        )

    def get(self, queue_id: str, expand: str | None = None) -> Queue:
        """``GET /queues/{queue_id}`` → a single :class:`Queue`.

        ``queue_id`` is the queue key (case-sensitive) or numeric id. Pass ``expand`` to include
        extra blocks, e.g. ``expand="all"`` (or ``projects,components,versions,types,team,
        workflows,fields,issueTypesConfig``).

        Args:
            queue_id: The queue's key or numeric id.
            expand: Extra blocks to include; ``None`` includes none.

        Returns:
            The queue.

        Examples:
            >>> tracker.queues.get("TEST", expand="all").key
            'TEST'
        """
        return self._session.send(endpoints.get_queue(queue_id, expand=expand))

    def tags(self, queue_id: str) -> ItemList[str]:
        """``GET /queues/{queue_id}/tags`` → the queue's tag names as a flat string array.

        Args:
            queue_id: The queue's key or numeric id.

        Returns:
            The queue's tag names.

        Examples:
            >>> tracker.queues.tags("TAGQ").root
            ['tag1', 'tag2']
        """
        return self._session.send(endpoints.list_tags(queue_id))

    def versions(self, queue_id: str) -> ItemList[QueueVersionInfo]:
        """``GET /queues/{queue_id}/versions`` → the queue's versions.

        Args:
            queue_id: The queue's key or numeric id.

        Returns:
            The queue's versions.

        Examples:
            >>> tracker.queues.versions("VERQ").root[0].name
            'v0.1'
        """
        return self._session.send(endpoints.list_versions(queue_id))

    def fields(self, queue_id: str) -> ItemList[QueueField]:
        """``GET /queues/{queue_id}/fields`` → the queue's required/local fields.

        Args:
            queue_id: The queue's key or numeric id.

        Returns:
            The queue's fields.

        Examples:
            >>> tracker.queues.fields("FLDQ").root[0].id
            'myfield'
        """
        return self._session.send(endpoints.list_fields(queue_id))

    def create(self, body: QueueCreate) -> Queue:
        """Create a queue from a typed ``QueueCreate`` body. Returns the created ``Queue``.

        Args:
            body: The new queue's key, name, lead and defaults.

        Returns:
            The created queue.

        Examples:
            >>> from ycli.yandex.tracker.queues.models import QueueCreate
            >>> new_queue = QueueCreate(
            ...     key="DESIGN",
            ...     name="Design",
            ...     lead="lead-login",
            ...     default_type="task",
            ...     default_priority="normal",
            ... )
            >>> tracker.queues.create(new_queue).key
            'DESIGN'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_queue(dumped))

    def delete(self, queue_id: str) -> None:
        """``DELETE /queues/{queue_id}`` — delete a queue (``204``, empty body).

        Args:
            queue_id: The queue's key or numeric id.

        Examples:
            >>> tracker.queues.delete("GONE")
        """
        self._session.send(endpoints.delete_queue(queue_id))

    def restore(self, queue_id: str) -> Queue:
        """``POST /queues/{queue_id}/_restore`` — restore a deleted queue (admin only).

        Returns the restored ``Queue``.

        Args:
            queue_id: The queue's key or numeric id.

        Returns:
            The restored queue.

        Examples:
            >>> tracker.queues.restore("BACK").key
            'BACK'
        """
        return self._session.send(endpoints.restore_queue(queue_id))

    def set_permissions(self, queue_id: str, body: QueuePermissionsUpdate) -> QueuePermissions:
        """Manage queue access from a typed ``QueuePermissionsUpdate`` body.

        Returns the queue's effective ``QueuePermissions`` after the change.

        Args:
            queue_id: The queue's key or numeric id.
            body: The permission changes, per category.

        Returns:
            The queue's permissions after the change.

        Examples:
            >>> from ycli.yandex.tracker.queues.models import (
            ...     QueuePermissionScope,
            ...     QueuePermissionsUpdate,
            ... )
            >>> change = QueuePermissionsUpdate(create=QueuePermissionScope(roles=["author"]))
            >>> tracker.queues.set_permissions("PERM", change).version
            11
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.set_permissions(queue_id, dumped))

    def tag_remove(self, queue_id: str, body: QueueTagRemove) -> None:
        """Remove a tag from a queue (admin only; ``204``, empty body).

        Args:
            queue_id: The queue's key or numeric id.
            body: The tag to remove.

        Examples:
            >>> from ycli.yandex.tracker.queues.models import QueueTagRemove
            >>> tracker.queues.tag_remove("TAGGED", QueueTagRemove(tag="obsolete"))
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        self._session.send(endpoints.remove_tag(queue_id, dumped))

    def version_create(self, body: QueueVersionCreate) -> QueueVersionInfo:
        """Create a queue version from a typed ``QueueVersionCreate`` body.

        Returns the created ``QueueVersionInfo``.

        Args:
            body: The new version's queue and name.

        Returns:
            The created version.

        Examples:
            >>> from ycli.yandex.tracker.queues.models import QueueVersionCreate
            >>> tracker.queues.version_create(QueueVersionCreate(queue="RELQ", name="v2.0")).name
            'v2.0'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_version(dumped))

    def version_get(self, version_id: int, *, fields: str | None = None) -> QueueVersionInfo:
        """``GET /versions/{version_id}`` → one queue version.

        ``fields`` is a comma list of the fields to return (``name,dueDate,released``, …).

        Args:
            version_id: The version's id.
            fields: A comma list of the fields to return; ``None`` returns the defaults.

        Returns:
            The version.

        Examples:
            >>> tracker.queues.version_get(901, fields="name,dueDate,released").name
            'Release 1.0'
        """
        return self._session.send(endpoints.get_version(version_id, fields=fields))

    def version_edit(
        self, version_id: int, body: QueueVersionUpdate, *, fields: str | None = None
    ) -> QueueVersionInfo:
        """``PATCH /versions/{version_id}`` → change the set fields of a version.

        Args:
            version_id: The version's id.
            body: The fields to change.
            fields: A comma list of the fields to return; ``None`` returns the defaults.

        Returns:
            The updated version.

        Examples:
            >>> from ycli.yandex.tracker.queues.models import QueueVersionUpdate
            >>> tracker.queues.version_edit(
            ...     903, QueueVersionUpdate(name="Release 1.1"), fields="name,description"
            ... ).version
            2
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_version(version_id, dumped, fields=fields))

    def version_delete(self, version_id: int) -> None:
        """``DELETE /versions/{version_id}`` → 204; raises on non-2xx.

        Args:
            version_id: The version's id.

        Examples:
            >>> tracker.queues.version_delete(905)
        """
        self._session.send(endpoints.delete_version(version_id))

    def user_permissions(self, queue_id: str, user_id: str) -> QueueUserAccess:
        """``GET /queues/{queue_id}/permissions/users/{user_id}`` → what a user may do in a queue.

        ``user_id`` is a login or a numeric uid.

        Args:
            queue_id: The queue's key or numeric id.
            user_id: The user's login or numeric uid.

        Returns:
            The user's rights in the queue.

        Examples:
            >>> tracker.queues.user_permissions("PERMQ", "carol").user.display
            'Carol'
        """
        return self._session.send(endpoints.get_user_access(queue_id, user_id))

    def group_permissions(self, queue_id: str, group_id: int) -> QueueGroupAccess:
        """``GET /queues/{queue_id}/permissions/groups/{group_id}`` → what a group may do.

        Args:
            queue_id: The queue's key or numeric id.
            group_id: The group's id.

        Returns:
            The group's rights in the queue.

        Examples:
            >>> tracker.queues.group_permissions("PERMG", 77).group.display
            'Editors'
        """
        return self._session.send(endpoints.get_group_access(queue_id, group_id))
