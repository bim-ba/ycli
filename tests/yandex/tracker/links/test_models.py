"""Property accessors on the Link model — populated and None branches."""

from ycli.yandex.tracker.links.models import Link


def test_link_properties_populated():
    link = Link.model_validate(
        {
            "id": 7,
            "type": {"id": "relates"},
            "object": {"key": "DE-2", "display": "Other"},
        }
    )
    assert link.type_id == "relates"
    assert link.object_key == "DE-2"
    assert link.object_display == "Other"


def test_link_properties_none():
    link = Link.model_validate({"id": 7})
    assert link.type_id is None
    assert link.object_key is None
    assert link.object_display is None
