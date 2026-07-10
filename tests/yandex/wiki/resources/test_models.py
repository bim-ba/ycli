"""Wiki page resource models — the {type, item} envelope over attachments and grids."""

from ycli.yandex.wiki.resources.models import ResourceItem, ResourceItemList, ResourcesResponse


def test_resource_item_keeps_payload_verbatim():
    item = ResourceItem.model_validate(
        {"type": "attachment", "item": {"name": "d.png", "size": "10"}}
    )
    assert item.type == "attachment"
    assert item.item == {"name": "d.png", "size": "10"}


def test_resource_item_defaults_when_empty():
    item = ResourceItem.model_validate({})
    assert item.type is None and item.item == {}


def test_resources_response_parses_results():
    resp = ResourcesResponse.model_validate(
        {"results": [{"type": "grid", "item": {"id": "g1"}}], "next_cursor": "c1"}
    )
    assert resp.results[0].type == "grid" and resp.next_cursor == "c1"


def test_resource_item_list_wraps_flat_root():
    lst = ResourceItemList([ResourceItem(type="grid", item={})])
    assert lst.root[0].type == "grid"
