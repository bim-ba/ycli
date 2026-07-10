"""TDD for ResourcesClient — cursor draining + query passthrough, mocked with `responses`."""

import requests
import responses

from ycli.yandex.wiki.resources.client import ResourcesClient
from ycli.yandex.wiki.resources.models import ResourceItemList

BASE = "https://api.wiki.yandex.net/v1"


def _client() -> ResourcesClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return ResourcesClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/resources",
        json={
            "results": [{"type": "attachment", "item": {"name": "d.png"}}],
            "next_cursor": None,
        },
        status=200,
    )
    out = _client().list(page_id=42)
    assert isinstance(out, ResourceItemList)
    assert out.root[0].type == "attachment"
    assert out.root[0].item["name"] == "d.png"
    assert responses.calls[0].request.params["page_size"] == "100"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_drains_next_cursor_and_passes_filters():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/resources",
        json={"results": [{"type": "attachment", "item": {}}], "next_cursor": "c1"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/resources",
        json={"results": [{"type": "grid", "item": {}}], "next_cursor": None},
        status=200,
    )
    out = _client().list(page_id=42, q="road", types="attachment,grid", order_by="created_at")
    assert [r.type for r in out.root] == ["attachment", "grid"]  # both pages drained
    assert len(responses.calls) == 2
    first = responses.calls[0].request.params  # ty: ignore[unresolved-attribute]
    assert first["q"] == "road"
    assert first["types"] == "attachment,grid"
    assert first["order_by"] == "created_at"
    assert responses.calls[1].request.params["cursor"] == "c1"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_limit_truncates_without_second_fetch():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/resources",
        json={
            "results": [{"type": "grid", "item": {}}, {"type": "attachment", "item": {}}],
            "next_cursor": "c1",
        },
        status=200,
    )
    out = _client().list(page_id=42, limit=1)
    assert [r.type for r in out.root] == ["grid"]  # capped before draining c1
    assert len(responses.calls) == 1
