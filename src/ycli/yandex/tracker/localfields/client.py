"""Declarative Tracker localFields client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.localfields.models import LocalField, LocalFieldList


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
