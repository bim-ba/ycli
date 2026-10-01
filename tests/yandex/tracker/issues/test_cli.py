"""TDD for the `tracker issues` CLI — model_dump_json output + write body assembly."""

import json

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

pytestmark = pytest.mark.integration

runner = CliRunner()


def test_get_dumps_issue_model(api):
    api.add(
        "GET",
        f"{BASE}/issues/DE-1",
        json={"key": "DE-1", "summary": "S", "type": {"key": "task"}},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "issues", "get", "DE-1"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["key"] == "DE-1"
    assert out["type"] == "task"


def test_list_builds_filter_body(api):
    api.add("POST", f"{BASE}/issues/_search", json=[{"key": "DE-1"}], status=200)
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "issues", "list", "--queue", "DE", "--status", "open"],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["key"] == "DE-1"
    assert api.body(0) == {"filter": {"queue": "DE", "status": "open"}}


def test_search_builds_query_body(api):
    api.add("POST", f"{BASE}/issues/_search", json=[{"key": "DE-9"}], status=200)
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "issues", "search", "Queue: DE AND Status: open"]
    )
    assert res.exit_code == 0
    assert api.body(0) == {"query": "Queue: DE AND Status: open"}


def test_count_query(api):
    api.add("POST", f"{BASE}/issues/_count", json=42, status=200)
    res = runner.invoke(cli.app, ["tracker", "issues", "count", "--query", "Queue: DE"])
    assert res.exit_code == 0
    assert res.stdout.strip() == "42"
    assert api.body(0) == {"query": "Queue: DE"}


def test_count_filters(api):
    api.add("POST", f"{BASE}/issues/_count", json=3, status=200)
    res = runner.invoke(
        cli.app, ["tracker", "issues", "count", "--queue", "DE", "--status", "open"]
    )
    assert res.exit_code == 0
    assert res.stdout.strip() == "3"
    assert api.body(0) == {"filter": {"queue": "DE", "status": "open"}}


def test_create_assembles_body_with_polymorphic_wrap_and_fields(api):
    api.add("POST", f"{BASE}/issues/", json={"key": "DE-10", "summary": "New"}, status=201)
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
    sent = api.body(0)
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


def test_update_assembles_partial_body(api):
    api.add("PATCH", f"{BASE}/issues/DE-5", json={"key": "DE-5", "summary": "U"}, status=200)
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
    sent = api.body(0)
    assert sent == {"summary": "U", "type": {"key": "bug"}}


def test_update_assembles_full_body(api):
    api.add("PATCH", f"{BASE}/issues/DE-5", json={"key": "DE-5"}, status=200)
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
    sent = api.body(0)
    assert sent == {
        "summary": "U",
        "type": {"key": "bug"},
        "priority": {"key": "normal"},
        "parent": "DE-1",
        "description": "body",
        "tags": ["a", "b"],
        "sprint": 123,
    }


def test_move_to_queue(api):
    api.add("POST", f"{BASE}/issues/TEST-1/_move", json={"key": "NEW-1"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "issues", "move", "TEST-1", "NEW"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["key"] == "NEW-1"
    assert "queue=NEW" in str(api.calls[0].url)


def test_suggest(api):
    api.add("GET", f"{BASE}/issues/_suggest", json=[{"key": "TEST-123"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "issues", "suggest", "fix bug"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["key"] == "TEST-123"
    assert "input=fix" in str(api.calls[0].url)


def test_scroll_clear(api):
    api.add("POST", f"{BASE}/system/search/scroll/_clear", status=200)
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "issues", "scroll-clear", "--pair", "scrollId=scrollToken"],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "cleared search scroll resources"}
    assert api.body(0) == {"scrollId": "scrollToken"}


def _page(start: int, count: int) -> list[dict]:
    return [{"key": f"DE-{n}"} for n in range(start, start + count)]


def test_list_caps_at_limit_and_warns_on_stderr(api):
    api.add("POST", f"{BASE}/issues/_search", json=_page(1, 100), headers={"X-Total-Pages": "3"})
    res = runner.invoke(
        cli.app, ["-o", "json", "tracker", "issues", "list", "--queue", "DE", "--limit", "5"]
    )
    assert res.exit_code == 0, res.output
    assert len(json.loads(res.stdout)) == 5
    assert "stopped at 5 items; more may be available" in res.stderr


def test_search_all_fetches_every_page(api):
    api.add("POST", f"{BASE}/issues/_search", json=_page(1, 100), headers={"X-Total-Pages": "2"})
    api.add("POST", f"{BASE}/issues/_search", json=_page(101, 1), headers={"X-Total-Pages": "2"})
    res = runner.invoke(
        cli.app, ["-o", "json", "tracker", "issues", "search", "Queue: DE", "--all"]
    )
    assert res.exit_code == 0, res.output
    assert len(json.loads(res.stdout)) == 101
    assert res.stderr == ""
