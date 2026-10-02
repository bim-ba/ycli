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

        Returns:
            The global fields.

        Examples:
            >>> tracker.fields.list().root[0].id
            'ruName'
        """
        return self._session.send(endpoints.list_fields())

    def get(self, field_id: str) -> CustomField:
        """``GET /fields/{field_id}`` → parameters of one issue field.

        Args:
            field_id: The field's id.

        Returns:
            The field.

        Examples:
            >>> tracker.fields.get("enName").id
            'enName'
        """
        return self._session.send(endpoints.get_field(field_id))

    def create(self, body: FieldCreate) -> CustomField:
        """Create a global field from a typed ``FieldCreate`` body. Returns the ``CustomField``.

        Args:
            body: The new field's settings.

        Returns:
            The created field.

        Examples:
            >>> from ycli.yandex.tracker.fields.models import FieldCreate, LocalizedName
            >>> tracker.fields.create(
            ...     FieldCreate(
            ...         name=LocalizedName(ru="Поле"),
            ...         id="myField",
            ...         category="cat-1",
            ...         type="ru.yandex.startrek.core.fields.StringFieldType",
            ...     )
            ... ).id
            'myField'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_field(dumped))

    def edit(self, field_id: str, body: FieldUpdate, *, version: int | None = None) -> CustomField:
        """Edit field ``field_id`` from a typed ``FieldUpdate`` body (rename and/or options).

        ``version`` is the current field version; when set it is sent as ``?version=`` for
        optimistic locking (the API rejects a stale version).

        Args:
            field_id: The field's id.
            body: The fields to change.
            version: The field's current version, for optimistic locking.

        Returns:
            The updated field.

        Examples:
            >>> from ycli.yandex.tracker.fields.models import FieldUpdate, LocalizedName
            >>> tracker.fields.edit(
            ...     "ruName", FieldUpdate(name=LocalizedName(ru="Имя")), version=3
            ... ).id
            'ruName'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_field(field_id, dumped, version=version))

    def category_create(self, body: FieldCategoryCreate) -> FieldCategoryRecord:
        """Create a field category from a typed ``FieldCategoryCreate`` body.

        Args:
            body: The new category's settings.

        Returns:
            The created category.

        Examples:
            >>> from ycli.yandex.tracker.fields.models import FieldCategoryCreate, LocalizedName
            >>> tracker.fields.category_create(
            ...     FieldCategoryCreate(name=LocalizedName(ru="Своя"), order=400)
            ... ).id
            '604f99'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_category(dumped))

    def category_edit(
        self, category_id: str, body: FieldCategoryUpdate, *, version: int | None = None
    ) -> FieldCategoryRecord:
        """Edit field category ``category_id`` from a typed ``FieldCategoryUpdate`` body.

        ``version`` is the current category version; when set it is sent as ``?version=`` for
        optimistic locking.

        Args:
            category_id: The category's id.
            body: The fields to change.
            version: The category's current version, for optimistic locking.

        Returns:
            The updated category.

        Examples:
            >>> from ycli.yandex.tracker.fields.models import FieldCategoryUpdate
            >>> tracker.fields.category_edit(
            ...     "604f99", FieldCategoryUpdate(order=500), version=1
            ... ).version
            2
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_category(category_id, dumped, version=version))
