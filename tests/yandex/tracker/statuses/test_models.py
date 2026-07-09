"""Model-parse + Field-metadata coverage for the Tracker statuses models."""

from ycli.yandex.tracker.statuses.models import (
    LocalizedName,
    Status,
    StatusCreate,
    StatusList,
    StatusUpdate,
)


def test_status_parses_every_field():
    s = Status.model_validate(
        {
            "self": "https://api.tracker.yandex.net/v3/statuses/1",
            "id": 1,
            "version": 1,
            "key": "open",
            "name": "Открыт",
            "description": "Открыт",
            "order": 200,
            "type": "new",
        }
    )
    assert s.self_url.endswith("/statuses/1")  # ty: ignore[unresolved-attribute]
    assert s.id == 1 and s.version == 1 and s.key == "open"
    assert s.name == "Открыт" and s.description == "Открыт"
    assert s.order == 200 and s.type == "new"


def test_statuslist_is_flat_root_array():
    sl = StatusList.model_validate([{"key": "open"}, {"key": "closed"}])
    assert [s.key for s in sl.root] == ["open", "closed"]


def test_status_create_body_serializes_localized_name_by_alias():
    body = StatusCreate(
        key="pause", name=LocalizedName(ru="Пауза", en="On pause"), type="paused"
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {"key": "pause", "name": {"ru": "Пауза", "en": "On pause"}, "type": "paused"}


def test_status_update_omits_unset_fields():
    body = StatusUpdate(order=350).model_dump(by_alias=True, exclude_none=True)
    assert body == {"order": 350}


def test_every_status_field_has_description():
    for name, field in Status.model_fields.items():
        assert field.description, f"Status.{name} is missing Field(description=…)"


def test_every_write_body_field_has_description():
    for model in (LocalizedName, StatusCreate, StatusUpdate):
        for name, field in model.model_fields.items():
            assert field.description, f"{model.__name__}.{name} is missing Field(description=…)"
