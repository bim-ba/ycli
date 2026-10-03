"""Pydantic models for Tracker per-queue local fields (LocalField + nested + LocalFieldList).

Mirrors ``GET /queues/{id}/localFields`` (array) and
``GET /queues/{id}/localFields/{key}`` (single). Local fields are custom fields scoped to one
queue; the same object shape serves both endpoints.
"""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel
from ycli.yandex.tracker.models import (
    FieldCreate,
    FieldSchema,
    KeyedReference,
    LocalizedName,
    OptionsProviderInput,
    Reference,
)


class OptionsProvider(APIModel):
    """Allowed-values descriptor of a local field (the ``optionsProvider`` block).

    Examples:
        >>> OptionsProvider.model_validate(
        ...     {"type": "FixedListOptionsProvider", "values": ["a", "b"]}
        ... ).values
        ['a', 'b']
    """

    type: str | None = Field(default=None, description="Drop-down provider type of the field.")
    need_validation: bool | None = Field(
        default=None,
        alias="needValidation",
        description="Whether a submitted value is validated against the list (true) or not.",
    )
    values: list[str] = Field(
        default_factory=list, description="Allowed values offered by the drop-down."
    )


class QueryProvider(APIModel):
    """Query-language class of a local field (the ``queryProvider`` block; read-only via API).

    Examples:
        >>> QueryProvider.model_validate({"type": "StringOptionalQueryProvider"}).type
        'StringOptionalQueryProvider'
    """

    type: str | None = Field(default=None, description="Query-language class of the field.")


class LocalField(APIModel):
    """A local (per-queue) custom field.

    ``key`` is the field key you pass to ``localfields_get``; ``schema`` (exposed as
    ``field_schema``) describes the value type. Optional blocks (``optionsProvider``,
    ``category``, …) are lenient so partial responses stay valid.

    Examples:
        >>> LocalField.model_validate(
        ...     {"key": "loc_field_key", "name": "Loc field", "schema": {"type": "string"}}
        ... ).field_schema.type
        'string'
    """

    type: str | None = Field(default=None, description="Field type marker; 'local' for these.")
    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the field.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the field.")
    name: str | None = Field(default=None, description="Human-readable name of the field.")
    description: str | None = Field(default=None, description="Free-text description of the field.")
    key: str | None = Field(default=None, description="Key of the field (used to reference it).")
    version: int | None = Field(
        default=None, description="Field version; incremented on every change to the field."
    )
    field_schema: FieldSchema | None = Field(
        default=None, alias="schema", description="Value-type descriptor of the field."
    )
    readonly: bool | None = Field(
        default=None,
        description="Whether the value cannot be edited (true) or can be changed (false).",
    )
    options: bool | None = Field(
        default=None,
        description="Whether any value is allowed (true) or values are limited by org settings.",
    )
    suggest: bool | None = Field(
        default=None,
        description="Whether a search suggestion appears while entering the value (true) or not.",
    )
    options_provider: OptionsProvider | None = Field(
        default=None, alias="optionsProvider", description="Allowed-values descriptor of the field."
    )
    query_provider: QueryProvider | None = Field(
        default=None, alias="queryProvider", description="Query-language class of the field."
    )
    order: int | None = Field(
        default=None, description="Ordinal position of the field in the organisation's field list."
    )
    category: Reference | None = Field(default=None, description="Category the field belongs to.")
    queue: KeyedReference | None = Field(
        default=None, description="The queue this local field is attached to."
    )


class LocalFieldList(RootModel[list[LocalField]]):
    """A bare JSON array of local fields — the flat public shape of ``localfields.list()``.

    Examples:
        >>> LocalFieldList.model_validate([{"key": "loc_field_key"}]).root[0].key
        'loc_field_key'
    """


class LocalFieldUpdate(APIModel):
    """Typed request body for ``PATCH /queues/{id}/localFields/{key}`` (edit a local field).

    This endpoint has no ``?version=`` optimistic lock; only the fields that are set are sent.

    Examples:
        >>> LocalFieldUpdate(order=102).model_dump(by_alias=True, exclude_none=True)
        {'order': 102}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the local field."
    )
    category: str | None = Field(
        default=None, description="New category identifier (from GET /fields/categories)."
    )
    options_provider: OptionsProviderInput | None = Field(
        default=None,
        serialization_alias="optionsProvider",
        description="Replacement fixed drop-down values for the field.",
    )
    order: int | None = Field(
        default=None, description="New position of the field in the organisation's field list."
    )
    description: str | None = Field(default=None, description="New description of the local field.")
    readonly: bool | None = Field(
        default=None, description="Whether the value is read-only (true) or editable (false)."
    )
    visible: bool | None = Field(
        default=None, description="Whether the field is always shown in the interface."
    )
    hidden: bool | None = Field(
        default=None, description="Whether the field is fully hidden even when filled in."
    )


FieldCategory = Reference  # deprecated, removed in 0.38
FieldQueueRef = KeyedReference  # deprecated, removed in 0.38


LocalFieldCreate = FieldCreate  # deprecated, removed in 0.39
LocalFieldSchema = FieldSchema  # deprecated, removed in 0.39
