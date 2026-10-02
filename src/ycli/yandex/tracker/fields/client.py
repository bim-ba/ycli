"""Tracker global-fields client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.fields.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.fields import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.fields.models import (
        CustomField,
        FieldCategoryCreate,
        FieldCategoryRecord,
        FieldCategoryUpdate,
        FieldCreate,
        FieldList,
        FieldUpdate,
    )


class FieldsClient(Resource):
    """List, get, create and edit global fields; create and edit their categories."""

    def list(self) -> FieldList:
        """``GET /fields`` → all global fields of the organisation.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.list().root[0].id  # doctest: +SKIP
            'ruName'
        """
        return self._session.send(endpoints.list_fields())

    def get(self, field_id: str) -> CustomField:
        """``GET /fields/{field_id}`` → parameters of one issue field.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.get(field_id="ruName").id  # doctest: +SKIP
            'ruName'
        """
        return self._session.send(endpoints.get_field(field_id))

    def create(self, body: FieldCreate) -> CustomField:
        """Create a global field from a typed ``FieldCreate`` body. Returns the ``CustomField``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.create(
            ...     FieldCreate(name=LocalizedName(ru="Поле"), id="f", category="1", type="…")
            ... ).id  # doctest: +SKIP
            'f'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_field(dumped))

    def edit(self, field_id: str, body: FieldUpdate, *, version: int | None = None) -> CustomField:
        """Edit field ``field_id`` from a typed ``FieldUpdate`` body (rename and/or options).

        ``version`` is the current field version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.edit(
            ...     "ruName", FieldUpdate(name=LocalizedName(ru="Имя")), version=3
            ... ).id  # doctest: +SKIP
            'ruName'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_field(field_id, dumped, version=version))

    def category_create(self, body: FieldCategoryCreate) -> FieldCategoryRecord:
        """Create a field category from a typed ``FieldCategoryCreate`` body.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.category_create(
            ...     FieldCategoryCreate(name=LocalizedName(ru="Своя"), order=400)
            ... ).id  # doctest: +SKIP
            '604f9920d23cd5'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_category(dumped))

    def category_edit(
        self, category_id: str, body: FieldCategoryUpdate, *, version: int | None = None
    ) -> FieldCategoryRecord:
        """Edit field category ``category_id`` from a typed ``FieldCategoryUpdate`` body.

        ``version`` is the current category version; when set it is sent as ``?version=`` for
        optimistic locking.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.category_edit(
            ...     "1", FieldCategoryUpdate(order=400), version=1
            ... ).version  # doctest: +SKIP
            2
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_category(category_id, dumped, version=version))
