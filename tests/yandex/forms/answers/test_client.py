"""TDD for AnswersClient — returns the {columns, answers, next} envelope verbatim."""

import json
from urllib.parse import parse_qs, urlparse

import requests
import responses

from ycli.yandex.forms.answers.client import AnswersClient
from ycli.yandex.forms.answers.models import AnswersResponse

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


def _client() -> AnswersClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return AnswersClient(session=s)


@responses.activate
def test_list_returns_envelope_verbatim():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
            "answers": [{"id": 99, "created": "2026-01-01", "data": [{"value": "x"}]}],
            "next": None,
        },
        status=200,
    )
    ar = _client().list(SID)
    assert isinstance(ar, AnswersResponse)
    assert ar.columns[0].text == "T"
    assert ar.answers[0].id == 99 and ar.answers[0].data == [{"value": "x"}]
    assert ar.next is None
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/answers"


def _paginated_callback(request):
    """Two-page stub: page 1 hands a next_url carrying ``id=100``; page 2 drains it."""
    params = parse_qs(urlparse(request.url).query)
    if "id" not in params:
        body = {
            "columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
            "answers": [{"id": 1, "created": "2026-01-01", "data": [{"value": "a"}]}],
            "next": {"next_url": f"{BASE}/surveys/{SID}/answers?id=100&page_size=1"},
        }
    else:
        body = {
            "columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
            "answers": [{"id": 2, "created": "2026-01-02", "data": [{"value": "b"}]}],
            "next": None,
        }
    return (200, {}, json.dumps(body))


@responses.activate
def test_list_all_follows_next_url_and_concatenates():
    responses.add_callback(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        callback=_paginated_callback,
        content_type="application/json",
    )
    ar = _client().list_all(SID)
    assert isinstance(ar, AnswersResponse)
    # every page drained, answers concatenated in order
    assert [a.id for a in ar.answers] == [1, 2]
    assert ar.columns[0].text == "T"  # columns kept from the first page
    assert ar.next is None  # merged envelope is fully drained
    assert len(responses.calls) == 2  # page 1 + the followed next_url
    assert "id=100" in responses.calls[1].request.url  # followed the server's cursor verbatim


@responses.activate
def test_list_all_breaks_on_self_pointing_cursor():
    """A server whose next_url points at itself must terminate, not loop forever."""
    same = f"{BASE}/surveys/{SID}/answers?id=100"

    def cb(request):
        body = {
            "columns": [],
            "answers": [{"id": 1, "created": "x", "data": []}],
            "next": {"next_url": same},
        }  # every page hands back the SAME cursor
        return (200, {}, json.dumps(body))

    responses.add_callback(
        responses.GET, f"{BASE}/surveys/{SID}/answers", callback=cb, content_type="application/json"
    )
    ar = _client().list_all(SID)
    # page 1 (no id) + one follow of id=100; the second sighting of id=100 trips the guard
    assert len(responses.calls) == 2
    assert [a.id for a in ar.answers] == [1, 1]


@responses.activate
def test_list_all_single_page_makes_one_call():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={"columns": [], "answers": [{"id": 7, "created": "x", "data": []}], "next": None},
        status=200,
    )
    ar = _client().list_all(SID)
    assert [a.id for a in ar.answers] == [7]
    assert len(responses.calls) == 1  # no next_url → no extra request


@responses.activate
def test_list_all_respects_limit():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [{"id": 1, "slug": "c", "type": "string", "text": "C"}],
            "answers": [
                {"id": 1, "created": "x", "data": []},
                {"id": 2, "created": "x", "data": []},
            ],
            "next": {"next_url": f"surveys/{SID}/answers?id=2"},
        },
        status=200,
    )
    ar = _client().list_all(SID, limit=1)
    assert len(ar.answers) == 1
    assert ar.next is None
    assert len(responses.calls) == 1  # limit satisfied by page 1 — no second fetch


@responses.activate
def test_list_all_limit_spans_pages():
    """limit=3 forces a second-page fetch (page 1 has 2 answers) then truncates within page 2."""
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [{"id": 1, "slug": "c", "type": "string", "text": "C"}],
            "answers": [
                {"id": 1, "created": "x", "data": []},
                {"id": 2, "created": "x", "data": []},
            ],
            "next": {"next_url": f"{BASE}/surveys/{SID}/answers?id=2&page_size=2"},
        },
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [{"id": 1, "slug": "c", "type": "string", "text": "C"}],
            "answers": [
                {"id": 3, "created": "x", "data": []},
                {"id": 4, "created": "x", "data": []},
            ],
            "next": None,
        },
        status=200,
    )
    ar = _client().list_all(SID, limit=3)
    assert len(ar.answers) == 3  # page 1 (2) + page 2 first 1, truncated
    assert [a.id for a in ar.answers] == [1, 2, 3]
    assert ar.next is None
    assert len(responses.calls) == 2  # page boundary was crossed
