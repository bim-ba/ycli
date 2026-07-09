"""Declarative Tracker /queues client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.pagination import OffsetStrategy
from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.queues.models import (
    Queue,
    QueueCreate,
    QueueFieldList,
    QueueList,
    QueuePermissions,
    QueuePermissionsUpdate,
    QueueTagList,
    QueueTagRemove,
    QueueVersionCreate,
    QueueVersionInfo,
    QueueVersionInfoList,
)

_PAGE_SIZE = 50


class QueuesClient(TrackerResource):
    """Declarative HTTP for ``/queues`` (page-paginated list + single get)."""

    @uplink.returns.json()
    @uplink.get("queues/")
    def _list_page(
        self,
        page: uplink.Query = 1,  # ty: ignore[invalid-parameter-default]
        per_page: uplink.Query("perPage") = _PAGE_SIZE,  # ty: ignore[invalid-type-form]
    ) -> QueueList:  # ty: ignore[empty-body]
        """One raw page of queues (1-based ``page``, size ``perPage``); internal — use ``list``."""

    def list(self, *, limit: int | None = None) -> QueueList:
        """``GET /queues/`` → flat :class:`QueueList`, draining ``page``/``perPage`` internally.

        Capped at ``limit`` (``None`` = every queue). The API returns 50 queues per page and
        pages via ``page``/``perPage``; this advances the page number until a short page comes
        back. Note the trailing slash — ``GET /queues/`` (without it Tracker returns the single
        queue whose key is empty).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.list(limit=10).root[0].key  # doctest: +SKIP
            'TEST'
        """
        strategy = OffsetStrategy(extract=lambda page: page.root, page_size=_PAGE_SIZE)
        queues = strategy.collect(
            lambda offset: self._list_page(page=offset // _PAGE_SIZE + 1, per_page=_PAGE_SIZE),
            limit,
        )
        return QueueList(queues)

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}")
    def get(
        self,
        queue_id: uplink.Path,
        expand: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> Queue:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}`` → a single :class:`Queue`.

        ``queue_id`` is the queue key (case-sensitive) or numeric id. Pass ``expand`` to include
        extra blocks, e.g. ``expand="all"`` (or ``projects,components,versions,types,team,
        workflows,fields,issueTypesConfig``).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.get(queue_id="TEST", expand="all").name  # doctest: +SKIP
            'Test'
        """

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/tags")
    def tags(self, queue_id: uplink.Path) -> QueueTagList:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/tags`` → the queue's tag names as a flat string array.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.tags(queue_id="TEST").root[0]  # doctest: +SKIP
            'tag1'
        """

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/versions")
    def versions(self, queue_id: uplink.Path) -> QueueVersionInfoList:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/versions`` → the queue's versions.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.versions(queue_id="TEST").root[0].name  # doctest: +SKIP
            'v0.1'
        """

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/fields")
    def fields(self, queue_id: uplink.Path) -> QueueFieldList:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/fields`` → the queue's required/local fields.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.fields(queue_id="TEST").root[0].id  # doctest: +SKIP
            'myfield'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("queues/")
    def _create(self, body: uplink.Body) -> Queue:  # ty: ignore[empty-body]
        """``POST /queues/`` — create a queue from a ready JSON body (see ``create``)."""

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
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.delete("queues/{queue_id}")
    def delete(self, queue_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /queues/{queue_id}`` — delete a queue (``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.delete(queue_id="TEST").status_code  # doctest: +SKIP
            204
        """

    @uplink.returns.json()
    @uplink.post("queues/{queue_id}/_restore")
    def restore(self, queue_id: uplink.Path) -> Queue:  # ty: ignore[empty-body]
        """``POST /queues/{queue_id}/_restore`` — restore a deleted queue (admin only).

        Returns the restored ``Queue``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.restore(queue_id="TEST").key  # doctest: +SKIP
            'TEST'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("queues/{queue_id}/permissions")
    def _set_permissions(self, queue_id: uplink.Path, body: uplink.Body) -> QueuePermissions:  # ty: ignore[empty-body]
        """``PATCH /queues/{queue_id}/permissions`` from a ready body (see ``set_permissions``)."""

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
        return self._set_permissions(
            queue_id=queue_id, body=body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.json
    @uplink.post("queues/{queue_id}/tags/_remove")
    def _tag_remove(self, queue_id: uplink.Path, body: uplink.Body) -> requests.Response:  # ty: ignore[empty-body]
        """``POST /queues/{queue_id}/tags/_remove`` from a ready body (see ``tag_remove``)."""

    def tag_remove(self, queue_id: str, body: QueueTagRemove) -> requests.Response:
        """Remove a tag from a queue (admin only; ``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.queues.tag_remove(
            ...     "TEST", QueueTagRemove(tag="obsolete")
            ... ).status_code  # doctest: +SKIP
            204
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._tag_remove(queue_id, dumped)  # ty: ignore[too-many-positional-arguments]

    @uplink.returns.json()
    @uplink.json
    @uplink.post("versions/")
    def _version_create(self, body: uplink.Body) -> QueueVersionInfo:  # ty: ignore[empty-body]
        """``POST /versions/`` — create a queue version from a ready body (see wrapper)."""

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
        return self._version_create(body=body.model_dump(by_alias=True, exclude_none=True))
