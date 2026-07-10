"""Model-parse + Field-metadata coverage for the Tracker priorities write-body models."""

from ycli.yandex.tracker.priorities.models import (
    LocalizedName,
    Priority,
    PriorityCreate,
    PriorityList,
    PriorityUpdate,
)


def test_priority_and_list_parse():
    p = Priority.model_validate({"key": "normal", "display": "Normal"})
    assert p.key == "normal" and p.display == "Normal"
    pl = PriorityList.model_validate([{"key": "critical"}, {"key": "normal"}])
    assert [x.key for x in pl.root] == ["critical", "normal"]


def test_priority_create_body_serializes_localized_name():
    body = PriorityCreate(
        key="one", name=LocalizedName(ru="Низкий", en="Low"), order=60
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {"key": "one", "name": {"ru": "Низкий", "en": "Low"}, "order": 60}


def test_priority_create_omits_optional_order_and_description():
    body = PriorityCreate(key="one", name=LocalizedName(ru="Низкий")).model_dump(
        by_alias=True, exclude_none=True
    )
    assert body == {"key": "one", "name": {"ru": "Низкий"}}


def test_priority_update_omits_unset_fields():
    body = PriorityUpdate(description="Описание").model_dump(by_alias=True, exclude_none=True)
    assert body == {"description": "Описание"}


def test_every_write_body_field_has_description():
    for model in (LocalizedName, PriorityCreate, PriorityUpdate):
        for name, field in model.model_fields.items():
            assert field.description, f"{model.__name__}.{name} is missing Field(description=…)"
