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
