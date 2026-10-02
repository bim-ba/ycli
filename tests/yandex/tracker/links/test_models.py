"""Property accessors on the Link model — populated and None branches."""

from ycli.yandex.tracker.links.models import Link, LinkPage


def test_link_properties_populated():
    link = Link.model_validate(
        {
            "id": 7,
            "type": {"id": "relates"},
            "object": {"key": "DE-2", "display": "Other"},
        }
    )
    assert link.type == "relates"
    assert link.object_key == "DE-2"
    assert link.object_display == "Other"


def test_link_properties_none():
    link = Link.model_validate({"id": 7})
    assert link.type is None
    assert link.object_key is None
    assert link.object_display is None


def test_link_page_parses_the_paged_reply_with_its_extra_fields():
    page = LinkPage.model_validate(
        {
            "links": [
                {
                    "self": "https://api.tracker.yandex.net/v3/issues/JUNE-2/links/47001",
                    "id": 47001,
                    "type": {"id": "relates", "inward": "relates", "outward": "relates"},
                    "direction": "outward",
                    "object": {"key": "TREK-9844", "display": "Related issue"},
                    "createdBy": {"id": "11", "display": "Ann"},
                    "updatedBy": {"id": "12", "display": "Bob"},
                    "createdAt": "2017-06-11T05:16:01.421+0000",
                    "updatedAt": "2017-06-11T05:16:01.421+0000",
                    "assignee": {"id": "13", "display": "Cy"},
                    "status": {"id": "1", "key": "open", "display": "Open"},
                }
            ]
        }
    )
    link = page.links[0]
    assert (link.type, link.object_key, link.status) == ("relates", "TREK-9844", "open")
    assert (link.created_by, link.updated_by, link.assignee) == ("Ann", "Bob", "Cy")
