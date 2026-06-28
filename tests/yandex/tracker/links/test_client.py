"""TDD for LinksClient."""

import json

import requests
import responses

from ycli.yandex.tracker.links.client import LinksClient
from ycli.yandex.tracker.links.models import Link, LinkList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> LinksClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return LinksClient(session=s)


@responses.activate
def test_list_returns_linklist():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/links",
        json=[
            {
                "type": {"id": "relates"},
                "direction": "outward",
                "object": {"key": "DE-2", "display": "Other"},
            }
        ],
        status=200,
    )
    out = _client().list("DE-1")
    assert isinstance(out, LinkList)
    assert out.root[0].type_id == "relates" and out.root[0].object_key == "DE-2"


@responses.activate
def test_add_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/links",
        json={"id": 7, "type": {"id": "relates"}, "object": {"key": "DE-2"}},
        status=201,
    )
    lk = _client().add("DE-1", body={"relationship": "relates", "issue": "DE-2"})
    assert isinstance(lk, Link) and lk.id == 7
    assert json.loads(responses.calls[0].request.body) == {
        "relationship": "relates",
        "issue": "DE-2",
    }
