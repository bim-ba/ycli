"""Model parsing for Tracker global fields."""

from ycli.yandex.tracker.fields.models import CustomField, FieldList


def test_custom_field_parses_nested_schema_and_providers():
    field = CustomField.model_validate(
        {
            "self": "https://api.tracker.yandex.net/v3/fields/ruName",
            "id": "ruName",
            "key": "ruName",
            "version": 3,
            "schema": {"type": "array", "items": "string", "required": False},
            "readonly": False,
            "optionsProvider": {"type": "FixedListOptionsProvider", "values": ["a", "b"]},
            "category": {"id": "1", "display": "System"},
            "type": "standard",
        }
    )
    assert field.field_schema.items == "string"  # ty: ignore[unresolved-attribute]
    assert field.options_provider.values == ["a", "b"]  # ty: ignore[unresolved-attribute]
    assert field.category.display == "System"  # ty: ignore[unresolved-attribute]
    assert field.self_url.endswith("/fields/ruName")  # ty: ignore[unresolved-attribute]


def test_field_list_is_flat_array():
    fields = FieldList.model_validate([{"id": "summary"}, {"id": "status"}])
    assert [f.id for f in fields.root] == ["summary", "status"]
