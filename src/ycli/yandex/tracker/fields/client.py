"""Declarative Tracker global-fields client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.fields.models import (
    CustomField,
    FieldCategoryCreate,
    FieldCategoryRecord,
    FieldCategoryUpdate,
    FieldCreate,
    FieldList,
    FieldUpdate,
)


class FieldsClient(TrackerResource):
    """Declarative HTTP for ``/fields`` (global fields + their categories)."""

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

    @uplink.returns.json()
    @uplink.json
    @uplink.post("fields")
    def _create(self, body: uplink.Body) -> CustomField:  # ty: ignore[empty-body]
        """``POST /fields`` — create from a ready JSON body (see ``create``)."""

    def create(self, body: FieldCreate) -> CustomField:
        """Create a global field from a typed ``FieldCreate`` body. Returns the ``CustomField``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.create(
            ...     FieldCreate(name=LocalizedName(ru="Поле"), id="f", category="1", type="…")
            ... ).id  # doctest: +SKIP
            'f'
        """
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("fields/{field_id}")
    def _edit(
        self,
        field_id: uplink.Path,
        body: uplink.Body,
        version: uplink.Query("version") = None,  # ty: ignore[invalid-type-form]
    ) -> CustomField:  # ty: ignore[empty-body]
        """``PATCH /fields/{field_id}?version=`` — edit from a ready body (see ``edit``)."""

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
        return self._edit(
            field_id=field_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
            version=version,
        )

    @uplink.returns.json()
    @uplink.json
    @uplink.post("fields/categories")
    def _category_create(self, body: uplink.Body) -> FieldCategoryRecord:  # ty: ignore[empty-body]
        """``POST /fields/categories`` — create from a ready body (see ``category_create``)."""

    def category_create(self, body: FieldCategoryCreate) -> FieldCategoryRecord:
        """Create a field category from a typed ``FieldCategoryCreate`` body.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.fields.category_create(
            ...     FieldCategoryCreate(name=LocalizedName(ru="Своя"), order=400)
            ... ).id  # doctest: +SKIP
            '604f9920d23cd5'
        """
        return self._category_create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("fields/categories/{category_id}")
    def _category_edit(
        self,
        category_id: uplink.Path,
        body: uplink.Body,
        version: uplink.Query("version") = None,  # ty: ignore[invalid-type-form]
    ) -> FieldCategoryRecord:  # ty: ignore[empty-body]
        """``PATCH /fields/categories/{category_id}?version=`` — edit (see ``category_edit``)."""

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
        return self._category_edit(
            category_id=category_id,
            body=body.model_dump(by_alias=True, exclude_none=True),
            version=version,
        )
