"""TDD for the localfields models — the schema alias, nested blocks, and LocalFieldList."""

from ycli.yandex.tracker.localfields.models import (
    LocalField,
    LocalFieldList,
    LocalFieldSchema,
    OptionsProvider,
)


def test_local_field_parses_full_payload():
    f = LocalField.model_validate(
        {
            "type": "local",
            "self": "https://api.tracker.yandex.net/v3/queues/ORG/localFields/k",
            "id": "6054--k",
            "name": "Loc field",
            "description": "Field description",
            "key": "k",
            "version": 2,
            "schema": {"type": "string", "required": False},
            "readonly": False,
            "options": True,
            "suggest": True,
            "optionsProvider": {"type": "Fixed", "needValidation": False, "values": ["a"]},
            "queryProvider": {"type": "StringOptionalQueryProvider"},
            "order": 7,
            "category": {"id": "1", "display": "System"},
            "queue": {"id": "1", "key": "ORG", "display": "My queue"},
        }
    )
    assert f.type == "local"
    assert f.self_url is not None
    assert f.self_url.endswith("/localFields/k")
    assert f.version == 2 and f.order == 7
    assert f.field_schema is not None
    assert f.field_schema.type == "string"
    assert f.field_schema.required is False
    assert f.options_provider is not None
    assert f.options_provider.values == ["a"]
    assert f.options_provider.need_validation is False
    assert f.query_provider is not None
    assert f.query_provider.type == "StringOptionalQueryProvider"
    assert f.category is not None and f.queue is not None
    assert f.category.display == "System" and f.queue.key == "ORG"


def test_schema_alias_accepts_name_and_alias():
    # populated via the API alias "schema"
    field_schema = LocalField.model_validate({"schema": {"type": "array"}}).field_schema
    assert field_schema is not None
    assert field_schema.type == "array"
    # and via the python field name (populate_by_name)
    field = LocalField(field_schema=LocalFieldSchema(type="string"))  # ty: ignore[unknown-argument]
    assert field.field_schema is not None
    assert field.field_schema.type == "string"


def test_local_field_serializes_by_alias():
    f = LocalField.model_validate({"key": "k", "schema": {"type": "string"}})
    dumped = f.model_dump(by_alias=True)
    assert "schema" in dumped and "field_schema" not in dumped


def test_defaults_are_none_for_optional_blocks():
    f = LocalField.model_validate({"key": "k"})
    assert f.field_schema is None and f.options_provider is None
    assert f.category is None and f.queue is None


def test_options_provider_standalone():
    op = OptionsProvider.model_validate({"type": "Fixed", "values": ["x", "y"]})
    assert op.values == ["x", "y"] and op.need_validation is None


def test_local_field_list_root_model():
    lst = LocalFieldList.model_validate([{"key": "a"}, {"key": "b"}])
    assert [f.key for f in lst.root] == ["a", "b"]
