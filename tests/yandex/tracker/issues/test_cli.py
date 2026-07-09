"""TDD for the `tracker issues` CLI — model_dump_json output + write body assembly."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_get_dumps_issue_model():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1",
        json={"key": "DE-1", "summary": "S", "type": {"key": "task"}},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "issues", "get", "DE-1"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["key"] == "DE-1"
    assert out["type"] == "task"


@responses.activate
def test_list_builds_filter_body():
    responses.add(responses.POST, f"{BASE}/issues/_search", json=[{"key": "DE-1"}], status=200)
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "issues", "list", "--queue", "DE", "--status", "open"],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["key"] == "DE-1"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "filter": {"queue": "DE", "status": "open"}
    }


@responses.activate
def test_search_builds_query_body():
    responses.add(responses.POST, f"{BASE}/issues/_search", json=[{"key": "DE-9"}], status=200)
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "issues", "search", "Queue: DE AND Status: open"]
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {"query": "Queue: DE AND Status: open"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_count_query():
    responses.add(responses.POST, f"{BASE}/issues/_count", json=42, status=200)
    res = runner.invoke(cli.app, ["tracker", "issues", "count", "--query", "Queue: DE"])
    assert res.exit_code == 0
    assert res.stdout.strip() == "42"
    assert json.loads(responses.calls[0].request.body) == {"query": "Queue: DE"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_count_filters():
    responses.add(responses.POST, f"{BASE}/issues/_count", json=3, status=200)
    res = runner.invoke(
        cli.app, ["tracker", "issues", "count", "--queue", "DE", "--status", "open"]
    )
    assert res.exit_code == 0
    assert res.stdout.strip() == "3"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "filter": {"queue": "DE", "status": "open"}
    }


@responses.activate
def test_create_assembles_body_with_polymorphic_wrap_and_fields():
    responses.add(
        responses.POST, f"{BASE}/issues/", json={"key": "DE-10", "summary": "New"}, status=201
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "issues",
            "create",
            "--queue",
            "DE",
            "--summary",
            "New",
            "--type",
            "task",
            "--priority",
            "normal",
            "--parent",
            "DE-1",
            "--description",
            "body",
            "--tag",
            "a",
            "--tag",
            "b",
            "--field",
            "sprint=123",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["key"] == "DE-10"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {
        "queue": "DE",
        "summary": "New",
        "type": {"key": "task"},
        "priority": {"key": "normal"},
        "parent": "DE-1",
        "description": "body",
        "tags": ["a", "b"],
        "sprint": 123,
    }


@responses.activate
def test_update_assembles_partial_body():
    responses.add(
        responses.PATCH, f"{BASE}/issues/DE-5", json={"key": "DE-5", "summary": "U"}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "issues",
            "update",
            "DE-5",
            "--summary",
            "U",
            "--type",
            "bug",
        ],
    )
    assert res.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"summary": "U", "type": {"key": "bug"}}


@responses.activate
def test_update_assembles_full_body():
    responses.add(responses.PATCH, f"{BASE}/issues/DE-5", json={"key": "DE-5"}, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "issues",
            "update",
            "DE-5",
            "--summary",
            "U",
            "--type",
            "bug",
            "--priority",
            "normal",
            "--parent",
            "DE-1",
            "--description",
            "body",
            "--tag",
            "a",
            "--tag",
            "b",
            "--field",
            "sprint=123",
        ],
    )
    assert res.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {
        "summary": "U",
        "type": {"key": "bug"},
        "priority": {"key": "normal"},
        "parent": "DE-1",
        "description": "body",
        "tags": ["a", "b"],
        "sprint": 123,
    }


@responses.activate
def test_move_to_queue():
    responses.add(responses.POST, f"{BASE}/issues/TEST-1/_move", json={"key": "NEW-1"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "issues", "move", "TEST-1", "NEW"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["key"] == "NEW-1"
    assert "queue=NEW" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
