"""TDD for MacrosClient — list/get reads and create/edit/delete writes."""

import json

import requests
import responses

from ycli.yandex.tracker.macros.client import MacrosClient
from ycli.yandex.tracker.macros.models import Macro, MacroCreate, MacroList, MacroUpdate

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> MacrosClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return MacrosClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST/macros",
        json=[{"id": 3, "name": "a"}, {"id": 4, "name": "b"}],
        status=200,
    )
    out = _client().list("TEST")
    assert isinstance(out, MacroList)
    assert [m.name for m in out.root] == ["a", "b"]


@responses.activate
def test_get_returns_single_macro():
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST/macros/3",
        json={"id": 3, "name": "My macro", "body": "Hi"},
        status=200,
    )
    m = _client().get("TEST", 3)
    assert isinstance(m, Macro) and m.id == 3 and m.body == "Hi"


@responses.activate
def test_create_posts_typed_body():
    responses.add(
        responses.POST,
        f"{BASE}/queues/TEST/macros",
        json={"id": 3, "name": "Test macro"},
        status=201,
    )
    m = _client().create(
        "TEST", MacroCreate(name="Test macro", body="Hi", issue_update={"tags": {"add": "x"}})
    )
    assert isinstance(m, Macro) and m.id == 3
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Test macro",
        "body": "Hi",
        "issueUpdate": {"tags": {"add": "x"}},
    }


@responses.activate
def test_edit_patches_only_supplied_fields():
    responses.add(
        responses.PATCH,
        f"{BASE}/queues/TEST/macros/3",
        json={"id": 3, "name": "Renamed"},
        status=200,
    )
    m = _client().edit("TEST", 3, MacroUpdate(name="Renamed"))
    assert m.name == "Renamed"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"name": "Renamed"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete_issues_delete_and_returns_response():
    responses.add(responses.DELETE, f"{BASE}/queues/TEST/macros/3", status=204)
    resp = _client().delete("TEST", 3)
    assert isinstance(resp, requests.Response) and resp.status_code == 204
    assert responses.calls[0].request.method == "DELETE"
