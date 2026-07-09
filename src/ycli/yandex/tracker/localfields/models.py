"""Pydantic models for Tracker per-queue local fields (LocalField + nested + LocalFieldList).

Mirrors ``GET /queues/{id}/localFields`` (array) and
``GET /queues/{id}/localFields/{key}`` (single). Local fields are custom fields scoped to one
queue; the same object shape serves both endpoints.
"""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class LocalFieldSchema(APIModel):
    """Value-type descriptor of a local field (the ``schema`` block).

    Example:
        >>> LocalFieldSchema.model_validate({"type": "string", "required": False}).type
        'string'
    """

    type: str | None = Field(
        default=None,
        description="Value type: 'string' for a single value, 'array' for multiple values.",
    )
    items: str | None = Field(
        default=None, description="Element type of the values; present only for array fields."
    )
    required: bool | None = Field(
        default=None, description="Whether the field must be filled in (true) or is optional."
    )


class OptionsProvider(APIModel):
    """Allowed-values descriptor of a local field (the ``optionsProvider`` block).

    Example:
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

    Example:
        >>> QueryProvider.model_validate({"type": "StringOptionalQueryProvider"}).type
        'StringOptionalQueryProvider'
    """

    type: str | None = Field(default=None, description="Query-language class of the field.")


class FieldCategory(APIModel):
    """Category a local field belongs to (the ``category`` block).

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


class FieldQueueRef(APIModel):
    """Reference to the queue a local field is attached to (the ``queue`` block).

    Example:
        >>> FieldQueueRef.model_validate({"key": "ORG", "display": "My queue"}).key
        'ORG'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the queue.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the queue.")
    key: str | None = Field(default=None, description="Key of the queue (case-sensitive).")
    display: str | None = Field(default=None, description="Human-readable name of the queue.")


class LocalField(APIModel):
    """A local (per-queue) custom field.

    ``key`` is the field key you pass to ``localfields_get``; ``schema`` (exposed as
    ``field_schema``) describes the value type. Optional blocks (``optionsProvider``,
    ``category``, …) are lenient so partial responses stay valid.

    Example:
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
    field_schema: LocalFieldSchema | None = Field(
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
    category: FieldCategory | None = Field(
        default=None, description="Category the field belongs to."
    )
    queue: FieldQueueRef | None = Field(
        default=None, description="The queue this local field is attached to."
    )


class LocalFieldList(RootModel[list[LocalField]]):
    """A bare JSON array of local fields — the flat public shape of ``localfields.list()``.

    Example:
        >>> LocalFieldList.model_validate([{"key": "loc_field_key"}]).root[0].key
        'loc_field_key'
    """


class LocalizedName(APIModel):
    """A localized display name (the ``name`` object) — Russian and/or English text.

    Example:
        >>> LocalizedName(ru="Поле", en="Field").model_dump(exclude_none=True)
        {'ru': 'Поле', 'en': 'Field'}
    """

    ru: str | None = Field(default=None, description="Name in Russian.")
    en: str | None = Field(default=None, description="Name in English.")


class OptionsProviderInput(APIModel):
    """Typed ``optionsProvider`` block for a local-field create/edit body (a fixed drop-down).

    Example:
        >>> OptionsProviderInput(type="FixedListOptionsProvider", values=["a"]).model_dump()
        {'type': 'FixedListOptionsProvider', 'values': ['a']}
    """

    type: str = Field(
        description="Drop-down provider type, e.g. FixedListOptionsProvider or "
        "FixedUserListOptionsProvider."
    )
    values: list[str] = Field(description="Allowed values offered by the drop-down.")


class LocalFieldCreate(APIModel):
    """Typed request body for ``POST /queues/{id}/localFields`` (create a local field).

    Example:
        >>> LocalFieldCreate(
        ...     name=LocalizedName(ru="Поле"), id="loc", category="1", type="StringFieldType"
        ... ).model_dump(by_alias=True, exclude_none=True)
        {'name': {'ru': 'Поле'}, 'id': 'loc', 'category': '1', 'type': 'StringFieldType'}
    """

    name: LocalizedName = Field(description="Localized display name of the new local field.")
    id: str = Field(description="Identifier (key) of the new local field.")
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
    description: str | None = Field(default=None, description="Description of the local field.")
    readonly: bool | None = Field(
        default=None, description="Whether the value is read-only (true) or editable (false)."
    )


class LocalFieldUpdate(APIModel):
    """Typed request body for ``PATCH /queues/{id}/localFields/{key}`` (edit a local field).

    This endpoint has no ``?version=`` optimistic lock; only the fields that are set are sent.

    Example:
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
