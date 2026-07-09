"""Model-parse + Field-metadata coverage for the Tracker resolutions models."""

from ycli.yandex.tracker.resolutions.models import (
    LocalizedName,
    Resolution,
    ResolutionCreate,
    ResolutionList,
    ResolutionUpdate,
)


def test_resolution_parses_every_field():
    r = Resolution.model_validate(
        {
            "self": "https://api.tracker.yandex.net/v3/resolutions/1",
            "id": 1,
            "key": "fixed",
            "version": 1,
            "name": "Решен",
            "description": "Решен",
            "order": 0,
        }
    )
    assert r.self_url.endswith("/resolutions/1")  # ty: ignore[unresolved-attribute]
    assert r.id == 1 and r.key == "fixed" and r.version == 1
    assert r.name == "Решен" and r.description == "Решен" and r.order == 0


def test_resolutionlist_is_flat_root_array():
    rl = ResolutionList.model_validate([{"key": "fixed"}, {"key": "duplicate"}])
    assert [r.key for r in rl.root] == ["fixed", "duplicate"]


def test_resolution_create_body_serializes_localized_name():
    body = ResolutionCreate(
        key="wontFix", name=LocalizedName(ru="Отклонено", en="Won't fix")
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {"key": "wontFix", "name": {"ru": "Отклонено", "en": "Won't fix"}}


def test_resolution_update_omits_unset_fields():
    body = ResolutionUpdate(order=90).model_dump(by_alias=True, exclude_none=True)
    assert body == {"order": 90}


def test_every_resolution_field_has_description():
    for name, field in Resolution.model_fields.items():
        assert field.description, f"Resolution.{name} is missing Field(description=…)"


def test_every_write_body_field_has_description():
    for model in (LocalizedName, ResolutionCreate, ResolutionUpdate):
        for name, field in model.model_fields.items():
            assert field.description, f"{model.__name__}.{name} is missing Field(description=…)"
