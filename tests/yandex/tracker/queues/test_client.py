"""TDD for QueuesClient — list drains page/perPage pages; get returns one Queue."""

import requests
import responses

from ycli.yandex.tracker.queues.client import QueuesClient
from ycli.yandex.tracker.queues.models import Queue, QueueList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> QueuesClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return QueuesClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/queues/",
        json=[{"id": "3", "key": "TEST"}, {"id": "4", "key": "DEMO"}],
        status=200,
    )
    out = _client().list()
    assert isinstance(out, QueueList)
    assert [q.key for q in out.root] == ["TEST", "DEMO"]
    assert responses.calls[0].request.params["page"] == "1"  # ty: ignore[unresolved-attribute]
    assert responses.calls[0].request.params["perPage"] == "50"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_drains_two_offset_pages():
    full_page = [{"id": str(index), "key": f"Q{index}"} for index in range(50)]  # exactly page_size
    responses.add(responses.GET, f"{BASE}/queues/", json=full_page, status=200)
    responses.add(responses.GET, f"{BASE}/queues/", json=[{"id": "50", "key": "TAIL"}], status=200)
    out = _client().list()
    assert len(out.root) == 51 and out.root[-1].key == "TAIL"  # both pages drained
    assert len(responses.calls) == 2
    assert responses.calls[1].request.params["page"] == "2"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_respects_limit_without_extra_fetch():
    responses.add(
        responses.GET,
        f"{BASE}/queues/",
        json=[{"key": "A"}, {"key": "B"}, {"key": "C"}],
        status=200,
    )
    out = _client().list(limit=2)
    assert [q.key for q in out.root] == ["A", "B"]  # truncated to the cap
    assert len(responses.calls) == 1


@responses.activate
def test_get_returns_single_queue_with_expand():
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST",
        json={
            "id": "3",
            "key": "TEST",
            "name": "Test",
            "version": 5,
            "lead": {"id": "11", "display": "Ivan"},
            "defaultType": {"key": "task", "display": "Task"},
            "assignAuto": False,
            "issueTypes": [{"key": "task"}, {"key": "bug"}],
            "workflows": {"dev": [{"key": "task"}]},
        },
        status=200,
    )
    q = _client().get("TEST", expand="all")
    assert isinstance(q, Queue)
    assert q.key == "TEST" and q.version == 5
    assert q.lead.display == "Ivan"
    assert q.default_type.key == "task"
    assert [t.key for t in q.issue_types] == ["task", "bug"]
    assert q.workflows["dev"][0].key == "task"
    assert responses.calls[0].request.params["expand"] == "all"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_get_without_expand_sends_no_query():
    responses.add(responses.GET, f"{BASE}/queues/TEST", json={"id": "3", "key": "TEST"}, status=200)
    q = _client().get("TEST")
    assert q.key == "TEST"
    assert "expand" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]
