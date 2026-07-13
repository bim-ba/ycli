"""TDD for WorklogClient — writes + relative-paginated list draining ``id=<last id>``."""

import json
from urllib.parse import parse_qs, urlparse

import requests
import responses

from ycli.yandex.tracker.worklog.client import WorklogClient
from ycli.yandex.tracker.worklog.models import Worklog, WorklogList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> WorklogClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return WorklogClient(session=s)


def _worklog_page_callback(request):
    """Three-request drain: page 1 (no id) → id=6 page → id=7 empty page terminates."""
    cursor = parse_qs(urlparse(request.url).query).get("id", [None])[0]
    if cursor is None:
        body = [
            {"id": 5, "createdBy": {"display": "X"}, "duration": "PT2H"},
            {"id": 6, "duration": "PT1H"},
        ]
    elif cursor == "6":
        body = [{"id": 7, "duration": "PT30M"}]
    else:  # id=7 → nothing left → RelativeCursorStrategy stops
        body = []
    return (200, {}, json.dumps(body))


@responses.activate
def test_list_drains_pages_across_relative_cursor():
    responses.add_callback(
        responses.GET,
        f"{BASE}/issues/DE-1/worklog",
        callback=_worklog_page_callback,
        content_type="application/json",
    )
    out = _client().list("DE-1")
    assert isinstance(out, WorklogList)
    assert [w.duration for w in out.root] == ["PT2H", "PT1H", "PT30M"]  # pages joined in order
    assert out.root[0].created_by == "X"
    assert len(responses.calls) == 3  # page1 + id=6 page + id=7 empty page
    assert "perPage=100" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    assert "id=6" in responses.calls[1].request.url  # ty: ignore[unsupported-operator]
    assert "id=7" in responses.calls[2].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_list_respects_limit_within_first_page():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/worklog",
        json=[{"id": 5, "duration": "PT2H"}, {"id": 6, "duration": "PT1H"}],
        status=200,
    )
    out = _client().list("DE-1", limit=1)
    assert [w.id for w in out.root] == [5]  # truncated to the limit
    assert len(responses.calls) == 1  # limit satisfied by page 1 — no second fetch


@responses.activate
def test_list_clamps_per_page_to_a_small_limit():
    """A small ``limit`` narrows the first request's ``perPage`` instead of always asking 100."""
    responses.add(responses.GET, f"{BASE}/issues/DE-1/worklog", json=[], status=200)
    _client().list("DE-1", limit=3)
    assert responses.calls[0].request.params["perPage"] == "3"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_terminates_when_last_record_has_no_id():
    """A last record with a null id yields no cursor, so the walk stops after one page."""
    responses.add(
        responses.GET, f"{BASE}/issues/DE-1/worklog", json=[{"duration": "PT2H"}], status=200
    )
    out = _client().list("DE-1")
    assert [w.duration for w in out.root] == ["PT2H"]
    assert len(responses.calls) == 1


@responses.activate
def test_create_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/worklog",
        json={"id": 1, "duration": "PT2H"},
        status=201,
    )
    w = _client().create("DE-1", body={"duration": "PT2H"})
    assert isinstance(w, Worklog) and w.duration == "PT2H"
    assert responses.calls[0].request.method == "POST"
    assert json.loads(responses.calls[0].request.body) == {"duration": "PT2H"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_edit_patches_body():
    responses.add(
        responses.PATCH,
        f"{BASE}/issues/DE-1/worklog/1",
        json={"id": 1, "duration": "PT30M"},
        status=200,
    )
    w = _client().edit("DE-1", "1", body={"duration": "PT30M"})
    assert isinstance(w, Worklog) and w.duration == "PT30M"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"duration": "PT30M"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete_returns_none():
    responses.add(responses.DELETE, f"{BASE}/issues/DE-1/worklog/1", status=204)
    assert _client().delete("DE-1", "1") is None
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_search_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/worklog/_search",
        json=[{"id": 1, "duration": "PT2H"}],
        status=200,
    )
    out = _client().search(body={"createdBy": "veikus"})
    assert isinstance(out, WorklogList)
    assert out.root[0].duration == "PT2H"
    assert json.loads(responses.calls[0].request.body) == {"createdBy": "veikus"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_global_list_passes_repeated_created_at_query():
    responses.add(responses.GET, f"{BASE}/worklog", json=[{"id": 1, "duration": "P3W"}], status=200)
    out = _client().global_list(
        created_by="veikus", created_at=["from:2018-06-06", "to:2018-06-07"]
    )
    assert isinstance(out, WorklogList)
    assert out.root[0].duration == "P3W"
    url = responses.calls[0].request.url
    assert "createdBy=veikus" in url  # ty: ignore[unsupported-operator]
    assert "createdAt=from" in url and "createdAt=to" in url  # ty: ignore[unsupported-operator]
