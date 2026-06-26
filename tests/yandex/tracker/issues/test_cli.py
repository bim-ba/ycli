"""TDD for the `tracker issues` CLI — model_dump_json output + write body assembly."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.cli import app

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


def _stub() -> TrackerClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TrackerClient(session=s)


@responses.activate
def test_get_dumps_issue_model(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1",
                  json={"key": "DE-1", "summary": "S", "type": {"key": "task"}}, status=200)
    res = runner.invoke(app, ["get", "DE-1"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["key"] == "DE-1"
    assert out["type"] == {"key": "task"}  # full model, not flattened


@responses.activate
def test_full_dumps_raw_dict(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1",
                  json={"key": "DE-1", "extra": "field"}, status=200)
    res = runner.invoke(app, ["full", "DE-1"])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"key": "DE-1", "extra": "field"}


@responses.activate
def test_list_builds_filter_body(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/_search", json=[{"key": "DE-1"}], status=200)
    res = runner.invoke(app, ["list", "--queue", "DE", "--status", "open"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["key"] == "DE-1"
    assert json.loads(responses.calls[0].request.body) == {"filter": {"queue": "DE", "status": "open"}}


@responses.activate
def test_search_builds_query_body(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/_search", json=[{"key": "DE-9"}], status=200)
    res = runner.invoke(app, ["search", "Queue: DE AND Status: open"])
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {"query": "Queue: DE AND Status: open"}


@responses.activate
def test_count_query(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/_count", json=42, status=200)
    res = runner.invoke(app, ["count", "--query", "Queue: DE"])
    assert res.exit_code == 0
    assert res.stdout.strip() == "42"
    assert json.loads(responses.calls[0].request.body) == {"query": "Queue: DE"}


@responses.activate
def test_count_filters(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/_count", json=3, status=200)
    res = runner.invoke(app, ["count", "--queue", "DE", "--status", "open"])
    assert res.exit_code == 0
    assert res.stdout.strip() == "3"
    assert json.loads(responses.calls[0].request.body) == {"filter": {"queue": "DE", "status": "open"}}


@responses.activate
def test_create_assembles_body_with_polymorphic_wrap_and_fields(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/", json={"key": "DE-10", "summary": "New"}, status=201)
    res = runner.invoke(app, [
        "create", "--queue", "DE", "--summary", "New", "--type", "task",
        "--priority", "normal", "--parent", "DE-1", "--description", "body",
        "--tag", "a", "--tag", "b", "--field", "sprint=123",
    ])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["key"] == "DE-10"
    sent = json.loads(responses.calls[0].request.body)
    # PROVEN production shapes: queue + parent bare strings; type/priority wrapped.
    assert sent == {
        "queue": "DE", "summary": "New", "type": {"key": "task"},
        "priority": {"key": "normal"}, "parent": "DE-1", "description": "body",
        "tags": ["a", "b"], "sprint": 123,
    }


@responses.activate
def test_update_assembles_partial_body(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.PATCH, f"{BASE}/issues/DE-5", json={"key": "DE-5", "summary": "U"}, status=200)
    res = runner.invoke(app, ["update", "DE-5", "--summary", "U", "--type", "bug"])
    assert res.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)
    assert sent == {"summary": "U", "type": {"key": "bug"}}  # only supplied fields


@responses.activate
def test_update_assembles_full_body(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.PATCH, f"{BASE}/issues/DE-5", json={"key": "DE-5"}, status=200)
    res = runner.invoke(app, [
        "update", "DE-5", "--summary", "U", "--type", "bug",
        "--priority", "normal", "--parent", "DE-1", "--description", "body",
        "--tag", "a", "--tag", "b", "--field", "sprint=123",
    ])
    assert res.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)
    assert sent == {
        "summary": "U", "type": {"key": "bug"}, "priority": {"key": "normal"},
        "parent": "DE-1", "description": "body", "tags": ["a", "b"], "sprint": 123,
    }
