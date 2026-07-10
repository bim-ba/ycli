"""Declarative Tracker localFields client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.localfields.models import (
    LocalField,
    LocalFieldCreate,
    LocalFieldList,
    LocalFieldUpdate,
)


class LocalFieldsClient(TrackerResource):
    """Declarative HTTP for ``/queues/{id}/localFields`` (per-queue custom fields)."""

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/localFields")
    def list(self, queue_id: uplink.Path) -> LocalFieldList:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/localFields`` → the queue's local fields.

        ``queue_id`` is the queue key (case-sensitive) or numeric id. Local fields are custom
        fields scoped to a single queue; the response is a bare JSON array.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.localfields.list(queue_id="ORG").root[0].key  # doctest: +SKIP
            'loc_field_key'
        """

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/localFields/{field_key}")
    def get(self, queue_id: uplink.Path, field_key: uplink.Path) -> LocalField:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/localFields/{field_key}`` → one local field.

        ``field_key`` is the field key returned by :meth:`list`.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.localfields.get(
            ...     queue_id="ORG", field_key="loc_field_key"
            ... ).name  # doctest: +SKIP
            'loc_field_name'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("queues/{queue_id}/localFields")
    def _create(self, queue_id: uplink.Path, body: uplink.Body) -> LocalField:  # ty: ignore[empty-body]
        """``POST /queues/{queue_id}/localFields`` — create from a ready body (see ``create``)."""

    def create(self, queue_id: str, body: LocalFieldCreate) -> LocalField:
        """Create a local field in queue ``queue_id`` from a typed ``LocalFieldCreate`` body.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.localfields.create(
            ...     "ORG",
            ...     LocalFieldCreate(
            ...         name=LocalizedName(ru="Поле"), id="loc", category="1", type="…"
            ...     ),
            ... ).key  # doctest: +SKIP
            'loc'
        """
        return self._create(
            queue_id=queue_id, body=body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("queues/{queue_id}/localFields/{field_key}")
    def _edit(self, queue_id: uplink.Path, field_key: uplink.Path, body: uplink.Body) -> LocalField:  # ty: ignore[empty-body]
        """``PATCH /queues/{queue_id}/localFields/{field_key}`` — edit (see ``edit``)."""

    def edit(self, queue_id: str, field_key: str, body: LocalFieldUpdate) -> LocalField:
        """Edit local field ``field_key`` of queue ``queue_id`` from a typed ``LocalFieldUpdate``.

        This endpoint has no ``?version=`` optimistic lock; only the fields set on ``body`` are
        sent, so omitted fields stay unchanged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.localfields.edit(
            ...     "ORG", "loc_field_key", LocalFieldUpdate(order=102)
            ... ).order  # doctest: +SKIP
            102
        """
        return self._edit(
            queue_id=queue_id,
            field_key=field_key,
            body=body.model_dump(by_alias=True, exclude_none=True),
        )
