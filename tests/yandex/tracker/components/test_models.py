"""Model parsing for Tracker components (+ write-body models)."""

from ycli.yandex.tracker.components.models import (
    Component,
    ComponentCreate,
    ComponentList,
    ComponentUpdate,
)


def test_component_parses_queue_and_lead():
    component = Component.model_validate(
        {
            "self": "https://api.tracker.yandex.net/v3/components/1",
            "id": 1,
            "version": 3,
            "name": "Test",
            "queue": {"id": "1", "key": "ORG", "display": "My queue"},
            "description": "My component",
            "lead": {"id": "11", "display": "Ivan Ivanov", "passportUid": 11},
            "assignAuto": False,
        }
    )
    assert component.queue.display == "My queue"  # ty: ignore[unresolved-attribute]
    assert component.lead is not None
    assert component.lead.display == "Ivan Ivanov" and component.lead.passport_uid == 11
    assert component.assign_auto is False


def test_component_list_is_flat_array():
    components = ComponentList.model_validate([{"name": "A"}, {"name": "B"}])
    assert [c.name for c in components.root] == ["A", "B"]


def test_component_create_serializes_assign_auto_by_alias():
    body = ComponentCreate(name="UI", queue="TEST", lead="ivan", assign_auto=False).model_dump(
        by_alias=True, exclude_none=True
    )
    assert body == {"name": "UI", "queue": "TEST", "lead": "ivan", "assignAuto": False}


def test_component_update_omits_unset_fields():
    body = ComponentUpdate(name="New").model_dump(by_alias=True, exclude_none=True)
    assert body == {"name": "New"}


def test_every_write_body_field_has_description():
    for model in (ComponentCreate, ComponentUpdate):
        for name, field in model.model_fields.items():
            assert field.description, f"{model.__name__}.{name} is missing Field(description=…)"
