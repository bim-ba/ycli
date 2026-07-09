"""TDD for TriggersClient — get/webhook_log reads and create/edit writes."""

import json

import requests
import responses

from ycli.yandex.tracker.triggers.client import TriggersClient
from ycli.yandex.tracker.triggers.models import (
    Trigger,
    TriggerAction,
    TriggerCondition,
    TriggerCreate,
    TriggerUpdate,
    WebhookLogList,
)

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> TriggersClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TriggersClient(session=s)


@responses.activate
def test_get_returns_trigger():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/triggers/16",
        json={"id": 16, "name": "trigger", "active": True},
        status=200,
    )
    t = _client().get("DESIGN", 16)
    assert isinstance(t, Trigger) and t.id == 16 and t.active is True


@responses.activate
def test_create_posts_typed_body():
    responses.add(
        responses.POST, f"{BASE}/queues/DESIGN/triggers", json={"id": 16, "name": "T"}, status=200
    )
    t = _client().create(
        "DESIGN",
        TriggerCreate(
            name="T",
            actions=[TriggerAction(type="Transition", status={"key": "open"})],  # ty: ignore[unknown-argument]
            conditions=[TriggerCondition(type="CommentFullyMatchCondition", word="Open")],  # ty: ignore[unknown-argument]
        ),
    )
    assert isinstance(t, Trigger) and t.id == 16
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "T",
        "actions": [{"type": "Transition", "status": {"key": "open"}}],
        "conditions": [{"type": "CommentFullyMatchCondition", "word": "Open"}],
    }


@responses.activate
def test_edit_sends_version_query_and_body():
    responses.add(
        responses.PATCH,
        f"{BASE}/queues/DESIGN/triggers/16",
        json={"id": 16, "active": False},
        status=200,
    )
    t = _client().edit("DESIGN", 16, TriggerUpdate(active=False), version=1)
    assert t.active is False
    assert responses.calls[0].request.method == "PATCH"
    assert responses.calls[0].request.params["version"] == "1"  # ty: ignore[unresolved-attribute]
    assert json.loads(responses.calls[0].request.body) == {"active": False}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_edit_without_version_sends_no_query():
    responses.add(responses.PATCH, f"{BASE}/queues/DESIGN/triggers/16", json={"id": 16}, status=200)
    _client().edit("DESIGN", 16, TriggerUpdate(name="Renamed"))
    assert "version" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]


@responses.activate
def test_webhook_log_returns_list_with_params():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DEV/triggers/6/webhooks/log",
        json=[{"id": "x", "duration": 235}],
        status=200,
    )
    out = _client().webhook_log("DEV", 6, issue_id="DEV-123", limit=100)
    assert isinstance(out, WebhookLogList) and out.root[0].duration == 235
    assert responses.calls[0].request.params["issueId"] == "DEV-123"  # ty: ignore[unresolved-attribute]
    assert responses.calls[0].request.params["limit"] == "100"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_webhook_log_without_params_sends_none():
    responses.add(responses.GET, f"{BASE}/queues/DEV/triggers/6/webhooks/log", json=[], status=200)
    _client().webhook_log("DEV", 6)
    assert "issueId" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]
    assert "limit" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]
