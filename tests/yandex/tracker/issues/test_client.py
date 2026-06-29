"""TDD for IssuesClient — pure declarative endpoints, mocked with `responses`."""

import json

import requests
import responses

from ycli.yandex.tracker.issues.client import IssuesClient
from ycli.yandex.tracker.issues.models import Issue, IssueList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> IssuesClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return IssuesClient(session=s)


@responses.activate
def test_get_deserializes_issue():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1",
        json={"key": "DE-1", "summary": "S", "type": {"key": "task"}},
        status=200,
    )
    i = _client().get("DE-1")
    assert isinstance(i, Issue)
    assert i.key == "DE-1" and i.type_key == "task"


@responses.activate
def test_search_returns_issuelist():
    responses.add(
        responses.POST,
        f"{BASE}/issues/_search",
        json=[{"key": "DE-1"}, {"key": "DE-2"}],
        status=200,
    )
    out = _client().search(body={"filter": {"queue": "DE"}})
    assert isinstance(out, IssueList)
    assert [i.key for i in out.root] == ["DE-1", "DE-2"]
    assert json.loads(responses.calls[0].request.body) == {"filter": {"queue": "DE"}}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_count_returns_int():
    responses.add(responses.POST, f"{BASE}/issues/_count", json=7, status=200)
    assert _client().count(body={"filter": {"queue": "DE"}}) == 7


@responses.activate
def test_create_posts_body():
    responses.add(
        responses.POST, f"{BASE}/issues/", json={"key": "DE-10", "summary": "New"}, status=201
    )
    i = _client().create(body={"queue": "DE", "summary": "New"})
    assert i.key == "DE-10"
    assert json.loads(responses.calls[0].request.body) == {"queue": "DE", "summary": "New"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_update_patches_body():
    responses.add(
        responses.PATCH,
        f"{BASE}/issues/DE-5",
        json={"key": "DE-5", "summary": "Updated"},
        status=200,
    )
    i = _client().update("DE-5", body={"summary": "Updated"})
    assert i.summary == "Updated"
    assert responses.calls[0].request.method == "PATCH"
