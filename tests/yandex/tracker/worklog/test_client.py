"""TDD for WorklogClient."""

import json

import requests
import responses

from ycli.yandex.tracker.worklog.client import WorklogClient
from ycli.yandex.tracker.worklog.models import Worklog, WorklogList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> WorklogClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return WorklogClient(session=s)


@responses.activate
def test_list_returns_workloglist():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/worklog",
        json=[{"id": 5, "createdBy": {"display": "X"}, "duration": "PT2H"}],
        status=200,
    )
    out = _client().list("DE-1")
    assert isinstance(out, WorklogList)
    assert out.root[0].duration == "PT2H" and out.root[0].created_by == "X"


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
