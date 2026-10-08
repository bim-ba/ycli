"""Tracker global-fields client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.fields.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.fields import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.fields.models import (
        CustomField,
        FieldCategoryCreate,
        FieldCategoryRecord,
        FieldCategoryUpdate,
        FieldUpdate,
    )
    from ycli.yandex.tracker.models import FieldCreate


class FieldsClient(Resource):
    """List, get, create and update global fields; create and edit their categories."""

    def list(self) -> ItemList[CustomField]:
        """``GET /fields`` → all global fields of the organisation.

        Returns:
            The global fields.

        Examples:
            >>> tracker.fields.list().root[0].id
            'ruName'
        """
        return self._session.send(endpoints.list_())

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
        return self._session.send(endpoints.get(field_id))

    def create(self, body: FieldCreate) -> CustomField:
        """Create a global field from a typed ``FieldCreate`` body. Returns the ``CustomField``.

        A name is unique among the fields: one that is taken answers 422 (measured).

        Args:
            body: The new field's settings.

        Returns:
            The created field.

        Examples:
            >>> from ycli.yandex.tracker.models import FieldCreate, LocalizedName
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
        return self._session.send(endpoints.create(body))

    def update(
        self, field_id: str, body: FieldUpdate, *, version: int | None = None
    ) -> CustomField:
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
            >>> from ycli.yandex.tracker.models import LocalizedName
            >>> from ycli.yandex.tracker.fields.models import FieldUpdate
            >>> tracker.fields.update(
            ...     "ruName", FieldUpdate(name=LocalizedName(ru="Имя")), version=3
            ... ).id
            'ruName'
        """
        return self._session.send(endpoints.update(field_id, body, version=version))

    def categories_create(self, body: FieldCategoryCreate) -> FieldCategoryRecord:
        """Create a field category from a typed ``FieldCategoryCreate`` body.

        Args:
            body: The new category's settings.

        Returns:
            The created category.

        Examples:
            >>> from ycli.yandex.tracker.models import LocalizedName
            >>> from ycli.yandex.tracker.fields.models import FieldCategoryCreate
            >>> tracker.fields.categories_create(
            ...     FieldCategoryCreate(name=LocalizedName(ru="Своя"), order=400)
            ... ).id
            '604f99'
        """
        return self._session.send(endpoints.categories_create(body))

    def categories_update(
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
            >>> tracker.fields.categories_update(
            ...     "604f99", FieldCategoryUpdate(order=500), version=1
            ... ).version
            2
        """
        return self._session.send(endpoints.categories_update(category_id, body, version=version))
