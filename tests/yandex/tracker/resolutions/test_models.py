"""Model-parse + Field-metadata coverage for the Tracker resolutions models."""

from ycli.yandex.tracker.resolutions.models import Resolution, ResolutionList


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


def test_every_resolution_field_has_description():
    for name, field in Resolution.model_fields.items():
        assert field.description, f"Resolution.{name} is missing Field(description=…)"
