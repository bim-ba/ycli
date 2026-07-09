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
    values: list[str] = Field(
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
