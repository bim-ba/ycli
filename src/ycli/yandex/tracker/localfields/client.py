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

        Args:
            queue_id: The queue's key or numeric id.

        Returns:
            The queue's local fields.

        Examples:
            >>> tracker.localfields.list("ORG").root[0].key
            'loc_field_key'
        """
        return self._session.send(endpoints.list_local_fields(queue_id))

    def get(self, queue_id: str, field_key: str) -> LocalField:
        """``GET /queues/{queue_id}/localFields/{field_key}`` → one local field.

        ``field_key`` is the field key returned by :meth:`list`.

        Args:
            queue_id: The queue's key or numeric id.
            field_key: The field's key.

        Returns:
            The local field.

        Examples:
            >>> tracker.localfields.get("OPS", "deadline_note").name
            'Deadline note'
        """
        return self._session.send(endpoints.get_local_field(queue_id, field_key))

    def create(self, queue_id: str, body: LocalFieldCreate) -> LocalField:
        """Create a local field in queue ``queue_id`` from a typed ``LocalFieldCreate`` body.

        Args:
            queue_id: The queue's key or numeric id.
            body: The new field's name, id, category and type.

        Returns:
            The created local field.

        Examples:
            >>> from ycli.yandex.tracker.models import LocalizedName
            >>> from ycli.yandex.tracker.localfields.models import LocalFieldCreate
            >>> new_field = LocalFieldCreate(
            ...     name=LocalizedName(ru="Поле", en="Field"),
            ...     id="loc_new",
            ...     category="cat-3",
            ...     type="ru.yandex.startrek.core.fields.StringFieldType",
            ... )
            >>> tracker.localfields.create("DEV", new_field).key
            'loc_new'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_local_field(queue_id, dumped))

    def edit(self, queue_id: str, field_key: str, body: LocalFieldUpdate) -> LocalField:
        """Edit local field ``field_key`` of queue ``queue_id`` from a typed ``LocalFieldUpdate``.

        This endpoint has no ``?version=`` optimistic lock; only the fields set on ``body`` are
        sent, so omitted fields stay unchanged.

        Args:
            queue_id: The queue's key or numeric id.
            field_key: The field's key.
            body: The fields to change.

        Returns:
            The updated local field.

        Examples:
            >>> from ycli.yandex.tracker.localfields.models import LocalFieldUpdate
            >>> tracker.localfields.edit("SUP", "loc_edit", LocalFieldUpdate(order=102)).order
            102
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_local_field(queue_id, field_key, dumped))
