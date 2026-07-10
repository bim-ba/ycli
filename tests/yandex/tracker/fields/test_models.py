"""Model parsing for Tracker global fields (+ write-body models)."""

from ycli.yandex.tracker.fields.models import (
    CustomField,
    FieldCategoryCreate,
    FieldCategoryRecord,
    FieldCategoryUpdate,
    FieldCreate,
    FieldList,
    FieldUpdate,
    LocalizedName,
    OptionsProviderInput,
)


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


def test_options_provider_accepts_integer_values():
    # The live global field `possibleSpam` returns optionsProvider.values as JSON integers.
    ints = CustomField.model_validate(
        {
            "id": "possibleSpam",
            "optionsProvider": {"type": "IntegerFieldOptionsProvider", "values": [0, 1]},
        }
    )
    assert ints.options_provider.values == [0, 1]  # ty: ignore[unresolved-attribute]
    # A string-valued options provider must still parse.
    strs = CustomField.model_validate(
        {
            "id": "priority",
            "optionsProvider": {"type": "FixedListOptionsProvider", "values": ["a", "b"]},
        }
    )
    assert strs.options_provider.values == ["a", "b"]  # ty: ignore[unresolved-attribute]


def test_field_list_is_flat_array():
    fields = FieldList.model_validate([{"id": "summary"}, {"id": "status"}])
    assert [f.id for f in fields.root] == ["summary", "status"]


def test_field_category_record_parses():
    rec = FieldCategoryRecord.model_validate(
        {"self": "https://x/fields/categories/1", "id": "1", "name": "System", "version": 2}
    )
    assert rec.id == "1" and rec.name == "System" and rec.version == 2
    assert rec.self_url.endswith("/categories/1")  # ty: ignore[unresolved-attribute]


def test_field_create_serializes_options_provider_by_alias():
    body = FieldCreate(
        name=LocalizedName(ru="Поле"),
        id="f",
        category="1",
        type="StringFieldType",
        options_provider=OptionsProviderInput(type="FixedListOptionsProvider", values=["a", "b"]),
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "name": {"ru": "Поле"},
        "id": "f",
        "category": "1",
        "type": "StringFieldType",
        "optionsProvider": {"type": "FixedListOptionsProvider", "values": ["a", "b"]},
    }


def test_field_update_covers_name_and_options_in_one_body():
    body = FieldUpdate(
        name=LocalizedName(en="Name"),
        options_provider=OptionsProviderInput(type="FixedListOptionsProvider", values=["x"]),
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "name": {"en": "Name"},
        "optionsProvider": {"type": "FixedListOptionsProvider", "values": ["x"]},
    }


def test_field_category_create_and_update_bodies():
    created = FieldCategoryCreate(name=LocalizedName(ru="Своя"), order=400).model_dump(
        by_alias=True, exclude_none=True
    )
    assert created == {"name": {"ru": "Своя"}, "order": 400}
    updated = FieldCategoryUpdate(description="new").model_dump(by_alias=True, exclude_none=True)
    assert updated == {"description": "new"}


def test_every_write_body_field_has_description():
    models = (
        LocalizedName,
        OptionsProviderInput,
        FieldCreate,
        FieldUpdate,
        FieldCategoryCreate,
        FieldCategoryUpdate,
        FieldCategoryRecord,
    )
    for model in models:
        for name, field in model.model_fields.items():
            assert field.description, f"{model.__name__}.{name} is missing Field(description=…)"
