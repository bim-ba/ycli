"""Tracker ``/queues/{id}/localFields`` client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.localfields.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.localfields import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.localfields.models import (
        LocalField,
        LocalFieldCreate,
        LocalFieldList,
        LocalFieldUpdate,
    )


class LocalFieldsClient(Resource):
    """List, get, create and edit a queue's local (queue-scoped custom) fields."""

    def list(self, queue_id: str) -> LocalFieldList:
        """``GET /queues/{queue_id}/localFields`` → the queue's local fields.

        ``queue_id`` is the queue key (case-sensitive) or numeric id. Local fields are custom
        fields scoped to a single queue; the response is a bare JSON array.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.localfields.list(queue_id="ORG").root[0].key  # doctest: +SKIP
            'loc_field_key'
        """
        return self._session.send(endpoints.list_local_fields(queue_id))

    def get(self, queue_id: str, field_key: str) -> LocalField:
        """``GET /queues/{queue_id}/localFields/{field_key}`` → one local field.

        ``field_key`` is the field key returned by :meth:`list`.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.localfields.get(
            ...     queue_id="ORG", field_key="loc_field_key"
            ... ).name  # doctest: +SKIP
            'loc_field_name'
        """
        return self._session.send(endpoints.get_local_field(queue_id, field_key))

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
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_local_field(queue_id, dumped))

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
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_local_field(queue_id, field_key, dumped))
