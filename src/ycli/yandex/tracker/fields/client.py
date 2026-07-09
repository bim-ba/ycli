"""Declarative Tracker global-fields client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.fields.models import CustomField, FieldList


class FieldsClient(TrackerResource):
    """Declarative HTTP for ``/fields`` (global organisation fields)."""

    @uplink.returns.json()
    @uplink.get("fields")
    def list(self) -> FieldList:  # ty: ignore[empty-body]
        """``GET /fields`` → all global fields of the organisation.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.list().root[0].id  # doctest: +SKIP
            'ruName'
        """

    @uplink.returns.json()
    @uplink.get("fields/{field_id}")
    def get(self, field_id: uplink.Path) -> CustomField:  # ty: ignore[empty-body]
        """``GET /fields/{field_id}`` → parameters of one issue field.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.get(field_id="ruName").id  # doctest: +SKIP
            'ruName'
        """
