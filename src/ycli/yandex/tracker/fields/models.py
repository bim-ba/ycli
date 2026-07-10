"""Pydantic models for Tracker global fields (CustomField + FieldList).

The single-record class is named ``CustomField`` (not ``Field``) so it never shadows
``pydantic.Field``, which every attribute in this module is declared with.
"""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class FieldSchema(APIModel):
    """Data-type descriptor of a field's value (the ``schema`` object).

    Example:
        >>> FieldSchema.model_validate({"type": "array", "items": "string"}).type
        'array'
    """

    type: str | None = Field(
        default=None,
        description="Value type: string for single-valued fields, array for multi-valued fields.",
    )
    items: str | None = Field(
        default=None, description="Element type; present only on multi-valued (array) fields."
    )
    required: bool | None = Field(
        default=None, description="Whether the field is mandatory (true) or optional (false)."
    )


class FieldProvider(APIModel):
    """A provider descriptor (suggest / options / query provider) attached to a field.

    Example:
        >>> FieldProvider.model_validate({"type": "FixedListOptionsProvider"}).type
        'FixedListOptionsProvider'
    """

    type: str | None = Field(
        default=None, description="Provider class name; cannot be changed via the API."
    )
    values: list[str | int] = Field(
        default_factory=list,
        description="Allowed field values; present only on an options provider.",
    )


class FieldCategory(APIModel):
    """The category a global field belongs to (the ``category`` object).

    Example:
        >>> FieldCategory.model_validate({"id": "1", "display": "System"}).display
        'System'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the category.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the field category.")
    display: str | None = Field(default=None, description="Human-readable name of the category.")


class CustomField(APIModel):
    """A global (organisation-wide) issue field — one ``/fields`` item / ``/fields/{id}`` object.

    Named ``CustomField`` rather than ``Field`` so it never shadows ``pydantic.Field``.

    Example:
        >>> CustomField.model_validate({"id": "ruName", "key": "ruName", "type": "standard"}).id
        'ruName'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the field.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the field.")
    name: str | None = Field(default=None, description="Display name of the field.")
    key: str | None = Field(default=None, description="Key of the field.")
    description: str | None = Field(default=None, description="Description of the field.")
    version: int | None = Field(
        default=None, description="Version of the field; each change increments the version number."
    )
    field_schema: FieldSchema | None = Field(
        default=None,
        alias="schema",
        description="Object describing the data type of the field's value.",
    )
    readonly: bool | None = Field(
        default=None,
        description="Whether the value can be edited: true if read-only, false if editable.",
    )
    options: bool | None = Field(
        default=None,
        description="Value constraint: true if any value is allowed, false if the list is limited.",
    )
    suggest: bool | None = Field(
        default=None,
        description="Whether a search suggestion appears while entering the field's value.",
    )
    suggest_provider: FieldProvider | None = Field(
        default=None,
        alias="suggestProvider",
        description="Object describing the search-suggestion provider class.",
    )
    options_provider: FieldProvider | None = Field(
        default=None,
        alias="optionsProvider",
        description="Object describing the allowed values of the field.",
    )
    query_provider: FieldProvider | None = Field(
        default=None,
        alias="queryProvider",
        description="Object describing the query-language class of the field.",
    )
    order: int | None = Field(
        default=None, description="Position of the field in the organisation's list of fields."
    )
    category: FieldCategory | None = Field(
        default=None, description="Object with information about the field's category."
    )
    type: str | None = Field(default=None, description="Type of the field.")


class FieldList(RootModel[list[CustomField]]):
    """A bare JSON array of global fields — the flat public shape of ``fields.list()``.

    Example:
        >>> FieldList.model_validate([{"id": "ruName"}]).root[0].id
        'ruName'
    """


class FieldCategoryRecord(APIModel):
    """A field category as returned by ``POST``/``PATCH /fields/categories`` (create/edit).

    Example:
        >>> FieldCategoryRecord.model_validate({"id": "1", "name": "System", "version": 1}).name
        'System'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the category.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the field category.")
    name: str | None = Field(default=None, description="Display name of the category.")
    version: int | None = Field(
        default=None, description="Version of the category; each change increments it."
    )


class LocalizedName(APIModel):
    """A localized display name (the ``name`` object) — Russian and/or English text.

    Example:
        >>> LocalizedName(ru="Поле", en="Field").model_dump(exclude_none=True)
        {'ru': 'Поле', 'en': 'Field'}
    """

    ru: str | None = Field(default=None, description="Name in Russian.")
    en: str | None = Field(default=None, description="Name in English.")


class OptionsProviderInput(APIModel):
    """Typed ``optionsProvider`` block for a field create/edit body (a fixed drop-down).

    Example:
        >>> OptionsProviderInput(type="FixedListOptionsProvider", values=["a", "b"]).model_dump()
        {'type': 'FixedListOptionsProvider', 'values': ['a', 'b']}
    """

    type: str = Field(
        description="Drop-down provider type, e.g. FixedListOptionsProvider or "
        "FixedUserListOptionsProvider."
    )
    values: list[str] = Field(description="Allowed values offered by the drop-down.")


class FieldCreate(APIModel):
    """Typed request body for ``POST /fields`` (create a global issue field).

    Example:
        >>> FieldCreate(
        ...     name=LocalizedName(ru="Поле"), id="myField", category="1", type="StringFieldType"
        ... ).model_dump(by_alias=True, exclude_none=True)
        {'name': {'ru': 'Поле'}, 'id': 'myField', 'category': '1', 'type': 'StringFieldType'}
    """

    name: LocalizedName = Field(description="Localized display name of the new field.")
    id: str = Field(description="Identifier (key) of the new field.")
    category: str = Field(
        description="Identifier of the field's category (from GET /fields/categories)."
    )
    type: str = Field(
        description="Field type, e.g. ru.yandex.startrek.core.fields.StringFieldType."
    )
    options_provider: OptionsProviderInput | None = Field(
        default=None,
        serialization_alias="optionsProvider",
        description="Fixed drop-down values, when the field is a limited-choice list.",
    )
    order: int | None = Field(
        default=None, description="Position of the field in the organisation's list of fields."
    )
    description: str | None = Field(default=None, description="Description of the field.")
    readonly: bool | None = Field(
        default=None, description="Whether the value is read-only (true) or editable (false)."
    )


class FieldUpdate(APIModel):
    """Typed request body for ``PATCH /fields/{id}?version=`` (rename and/or change options).

    Rename and change-options share one PATCH, so this one body covers both ``name`` and
    ``optionsProvider``; only the fields that are set are sent.

    Example:
        >>> FieldUpdate(name=LocalizedName(ru="Поле")).model_dump(by_alias=True, exclude_none=True)
        {'name': {'ru': 'Поле'}}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the field."
    )
    options_provider: OptionsProviderInput | None = Field(
        default=None,
        serialization_alias="optionsProvider",
        description="Replacement fixed drop-down values for the field.",
    )


class FieldCategoryCreate(APIModel):
    """Typed request body for ``POST /fields/categories`` (create a field category).

    Example:
        >>> FieldCategoryCreate(name=LocalizedName(ru="Своя"), order=400).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'name': {'ru': 'Своя'}, 'order': 400}
    """

    name: LocalizedName = Field(description="Localized display name of the new category.")
    order: int = Field(description="Weight controlling the category's display order (lower first).")
    description: str | None = Field(default=None, description="Description of the category.")


class FieldCategoryUpdate(APIModel):
    """Typed request body for ``PATCH /fields/categories/{id}?version=`` (edit a category).

    Only the fields that are set are sent, so omitted fields stay unchanged.

    Example:
        >>> FieldCategoryUpdate(order=400).model_dump(by_alias=True, exclude_none=True)
        {'order': 400}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the category."
    )
    order: int | None = Field(
        default=None, description="New weight controlling the category's display order."
    )
    description: str | None = Field(default=None, description="New description of the category.")
