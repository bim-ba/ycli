"""TDD for AutoactionsClient — get + two log reads and the create write."""

import json

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.autoactions.client import AutoactionsClient
from ycli.yandex.tracker.autoactions.models import (
    Autoaction,
    AutoactionAction,
    AutoactionCreate,
    AutoactionLogList,
    AutoactionRunList,
)


def _client() -> AutoactionsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return AutoactionsClient(session=s)


@responses.activate
def test_get_returns_autoaction():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/autoactions/9",
        json={"id": 9, "name": "auto", "active": True},
        status=200,
    )
    a = _client().get("DESIGN", 9)
    assert isinstance(a, Autoaction) and a.id == 9 and a.active is True


@responses.activate
def test_create_posts_typed_body():
    responses.add(
        responses.POST,
        f"{BASE}/queues/DESIGN/autoactions",
        json={"id": 9, "name": "A"},
        status=200,
    )
    a = _client().create(
        "DESIGN",
        AutoactionCreate(
            name="A",
            query="Status: Open",
            actions=[AutoactionAction(type="Transition", status={"key": "needInfo"})],  # ty: ignore[unknown-argument]
        ),
    )
    assert isinstance(a, Autoaction) and a.id == 9
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "A",
        "query": "Status: Open",
        "actions": [{"type": "Transition", "status": {"key": "needInfo"}}],
    }


@responses.activate
def test_logs_returns_run_summaries():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/autoactions/9/logs",
        json=[{"id": "x", "searchHits": 3}],
        status=200,
    )
    out = _client().logs("DESIGN", 9)
    assert isinstance(out, AutoactionLogList) and out.root[0].search_hits == 3


@responses.activate
def test_log_detail_returns_per_issue_outcomes():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/autoactions/9/logs/abc",
        json=[{"id": 0, "issueReference": {"key": "TEST-1"}, "status": {"value": "success"}}],
        status=200,
    )
    out = _client().log_detail("DESIGN", 9, "abc")
    assert isinstance(out, AutoactionRunList)
    assert out.root[0].issue_reference.key == "TEST-1" and out.root[0].status.value == "success"
