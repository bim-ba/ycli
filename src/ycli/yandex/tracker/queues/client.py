"""Tracker ``/queues`` client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.queues.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.queues import endpoints
from ycli.yandex.tracker.queues.models import QueueList

if TYPE_CHECKING:
    from ycli.yandex.tracker.queues.models import (
        Queue,
        QueueCreate,
        QueueFieldList,
        QueueGroupAccess,
        QueuePermissions,
        QueuePermissionsUpdate,
        QueueTagList,
        QueueTagRemove,
        QueueUserAccess,
        QueueVersionCreate,
        QueueVersionInfo,
        QueueVersionInfoList,
        QueueVersionUpdate,
    )


class QueuesClient(Resource):
    """List (page-paginated), get, create, delete and restore queues; tags, versions, access."""

    def list(self, *, limit: int | None = None) -> QueueList:
        """``GET /queues/`` → flat :class:`QueueList`, draining ``page``/``perPage`` internally.

        Capped at ``limit`` (``None`` = every queue). The API returns 50 queues per page; this
        advances the page number up to ``X-Total-Pages``, or until a short page comes back.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.list(limit=10).root[0].key  # doctest: +SKIP
            'TEST'
        """
        return QueueList(list(self._session.iterate(endpoints.list_queues(), limit=limit)))

    def get(self, queue_id: str, expand: str | None = None) -> Queue:
        """``GET /queues/{queue_id}`` → a single :class:`Queue`.

        ``queue_id`` is the queue key (case-sensitive) or numeric id. Pass ``expand`` to include
        extra blocks, e.g. ``expand="all"`` (or ``projects,components,versions,types,team,
        workflows,fields,issueTypesConfig``).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.get(queue_id="TEST", expand="all").name  # doctest: +SKIP
            'Test'
        """
        return self._session.send(endpoints.get_queue(queue_id, expand=expand))

    def tags(self, queue_id: str) -> QueueTagList:
        """``GET /queues/{queue_id}/tags`` → the queue's tag names as a flat string array.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.tags(queue_id="TEST").root[0]  # doctest: +SKIP
            'tag1'
        """
        return self._session.send(endpoints.list_tags(queue_id))

    def versions(self, queue_id: str) -> QueueVersionInfoList:
        """``GET /queues/{queue_id}/versions`` → the queue's versions.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.versions(queue_id="TEST").root[0].name  # doctest: +SKIP
            'v0.1'
        """
        return self._session.send(endpoints.list_versions(queue_id))

    def fields(self, queue_id: str) -> QueueFieldList:
        """``GET /queues/{queue_id}/fields`` → the queue's required/local fields.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.fields(queue_id="TEST").root[0].id  # doctest: +SKIP
            'myfield'
        """
        return self._session.send(endpoints.list_fields(queue_id))

    def create(self, body: QueueCreate) -> Queue:
        """Create a queue from a typed ``QueueCreate`` body. Returns the created ``Queue``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.create(
            ...     QueueCreate(
            ...         key="DESIGN",
            ...         name="Design",
            ...         lead="username",
            ...         default_type="task",
            ...         default_priority="normal",
            ...     )
            ... ).key  # doctest: +SKIP
            'DESIGN'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_queue(dumped))

    def delete(self, queue_id: str) -> None:
        """``DELETE /queues/{queue_id}`` — delete a queue (``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.delete(queue_id="TEST")  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_queue(queue_id))

    def restore(self, queue_id: str) -> Queue:
        """``POST /queues/{queue_id}/_restore`` — restore a deleted queue (admin only).

        Returns the restored ``Queue``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.restore(queue_id="TEST").key  # doctest: +SKIP
            'TEST'
        """
        return self._session.send(endpoints.restore_queue(queue_id))

    def set_permissions(self, queue_id: str, body: QueuePermissionsUpdate) -> QueuePermissions:
        """Manage queue access from a typed ``QueuePermissionsUpdate`` body.

        Returns the queue's effective ``QueuePermissions`` after the change.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.set_permissions(
            ...     "TEST", QueuePermissionsUpdate(create=QueuePermissionScope(roles=["author"]))
            ... ).version  # doctest: +SKIP
            11
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.set_permissions(queue_id, dumped))

    def tag_remove(self, queue_id: str, body: QueueTagRemove) -> None:
        """Remove a tag from a queue (admin only; ``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.tag_remove("TEST", QueueTagRemove(tag="obsolete"))  # doctest: +SKIP
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        self._session.send(endpoints.remove_tag(queue_id, dumped))

    def version_create(self, body: QueueVersionCreate) -> QueueVersionInfo:
        """Create a queue version from a typed ``QueueVersionCreate`` body.

        Returns the created ``QueueVersionInfo``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.version_create(
            ...     QueueVersionCreate(queue="TEST", name="v0.1")
            ... ).name  # doctest: +SKIP
            'v0.1'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_version(dumped))

    def version_get(self, version_id: int, *, fields: str | None = None) -> QueueVersionInfo:
        """``GET /versions/{version_id}`` → one queue version.

        ``fields`` is a comma list of the fields to return (``name,dueDate,released``, …).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.version_get(123).name  # doctest: +SKIP
            'v1.0'
        """
        return self._session.send(endpoints.get_version(version_id, fields=fields))

    def version_edit(
        self, version_id: int, body: QueueVersionUpdate, *, fields: str | None = None
    ) -> QueueVersionInfo:
        """``PATCH /versions/{version_id}`` → change the set fields of a version.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.version_edit(
            ...     123, QueueVersionUpdate(name="v1.1")
            ... ).version  # doctest: +SKIP
            2
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_version(version_id, dumped, fields=fields))

    def version_delete(self, version_id: int) -> None:
        """``DELETE /versions/{version_id}`` → 204; raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.version_delete(123)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_version(version_id))

    def user_permissions(self, queue_id: str, user_id: str) -> QueueUserAccess:
        """``GET /queues/{queue_id}/permissions/users/{user_id}`` → what a user may do in a queue.

        ``user_id`` is a login or a numeric uid.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.user_permissions("TEST", "alice").permissions.create  # doctest: +SKIP
        """
        return self._session.send(endpoints.get_user_access(queue_id, user_id))

    def group_permissions(self, queue_id: str, group_id: int) -> QueueGroupAccess:
        """``GET /queues/{queue_id}/permissions/groups/{group_id}`` → what a group may do.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.group_permissions("TEST", 5).permissions.read  # doctest: +SKIP
        """
        return self._session.send(endpoints.get_group_access(queue_id, group_id))
