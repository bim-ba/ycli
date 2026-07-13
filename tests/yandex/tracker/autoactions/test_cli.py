"""CLI tests for `tracker autoactions` (require the resource wired into the root app)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@responses.activate
def test_autoactions_get():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/autoactions/9",
        json={"id": 9, "name": "auto"},
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "autoactions", "get", "DESIGN", "9"]
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["name"] == "auto"


@responses.activate
def test_autoactions_create():
    responses.add(
        responses.POST,
        f"{BASE}/queues/DESIGN/autoactions",
        json={"id": 9, "name": "A"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "autoactions",
            "create",
            "DESIGN",
            "--name",
            "A",
            "--query",
            "Status: Open",
            "--action",
            '{"type": "Transition", "status": {"key": "needInfo"}}',
            "--calendar-id",
            "2",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 9
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "A",
        "query": "Status: Open",
        "actions": [{"type": "Transition", "status": {"key": "needInfo"}}],
        "calendar": {"id": 2},
    }


@responses.activate
def test_autoactions_logs():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/autoactions/9/logs",
        json=[{"id": "x", "searchHits": 3}],
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "autoactions", "logs", "DESIGN", "9"]
    )
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["searchHits"] == 3


@responses.activate
def test_autoactions_log_detail():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/autoactions/9/logs/abc",
        json=[{"id": 0, "status": {"value": "success"}}],
        status=200,
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "autoactions", "log-detail", "DESIGN", "9", "abc"],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["status"]["value"] == "success"
