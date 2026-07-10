"""TDD for BulkClient — responses stub + the poll() ``--wait`` path with an injected sleep."""

import json

import requests
import responses

from ycli.yandex.polling import poll
from ycli.yandex.tracker.bulk.client import BulkClient
from ycli.yandex.tracker.bulk.models import BulkChange, BulkIssueResultList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> BulkClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return BulkClient(session=session)


@responses.activate
def test_update_posts_body_and_returns_change():
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_update",
        json={"id": "1ab", "status": "CREATED"},
        status=201,
    )
    change = _client().update(
        body={"issues": ["TEST-1"], "values": {"priority": {"key": "blocker"}}}
    )
    assert isinstance(change, BulkChange)
    assert change.id == "1ab" and change.status == "CREATED"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "issues": ["TEST-1"],
        "values": {"priority": {"key": "blocker"}},
    }


@responses.activate
def test_move_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_move",
        json={"id": "2cd", "status": "CREATED"},
        status=201,
    )
    change = _client().move(body={"queue": "CHECK", "issues": ["TEST-1"]})
    assert change.id == "2cd"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "queue": "CHECK",
        "issues": ["TEST-1"],
    }


@responses.activate
def test_transition_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_transition",
        json={"id": "3ef", "status": "CREATED"},
        status=201,
    )
    change = _client().transition(body={"transition": "close", "issues": ["TEST-1"]})
    assert change.id == "3ef"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "transition": "close",
        "issues": ["TEST-1"],
    }


@responses.activate
def test_get_returns_status():
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab",
        json={"id": "1ab", "status": "COMPLETE"},
        status=200,
    )
    change = _client().get("1ab")
    assert change.is_terminal is True


@responses.activate
def test_issues_returns_result_list():
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab/issues",
        json=[{"issue": {"key": "TEST-1"}, "status": "FAILED"}],
        status=200,
    )
    out = _client().issues("1ab")
    assert isinstance(out, BulkIssueResultList)
    assert out.root[0].issue == "TEST-1"


@responses.activate
def test_wait_polls_get_until_terminal_status():
    """The ``--wait`` path: poll() re-reads GET /bulkchange/{id} until status is terminal.

    Two-status sequence (CREATED → COMPLETE) with a recorder ``sleep`` (no real waiting): the
    loop fetches twice, sleeps exactly once in between, and returns the terminal change.
    """
    responses.add(
        responses.GET, f"{BASE}/bulkchange/1ab", json={"id": "1ab", "status": "CREATED"}, status=200
    )
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab",
        json={"id": "1ab", "status": "COMPLETE"},
        status=200,
    )
    client = _client()
    slept: list[float] = []
    final = poll(
        lambda: client.get("1ab"),
        lambda change: change.is_terminal,
        sleep=slept.append,
    )
    assert final.status == "COMPLETE"
    assert final.is_terminal is True
    assert len(responses.calls) == 2  # fetched twice
    assert slept == [0.5]  # slept once between the two fetches (default backoff)
