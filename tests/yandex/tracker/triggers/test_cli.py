"""CLI tests for `tracker triggers` (require the resource wired into the root app)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@responses.activate
def test_triggers_get():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/triggers/16",
        json={"id": 16, "name": "trigger"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "triggers", "get", "DESIGN", "16"])
    assert res.exit_code == 0 and json.loads(res.stdout)["name"] == "trigger"


@responses.activate
def test_triggers_create():
    responses.add(
        responses.POST, f"{BASE}/queues/DESIGN/triggers", json={"id": 16, "name": "T"}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "triggers",
            "create",
            "DESIGN",
            "--name",
            "T",
            "--action",
            '{"type": "Transition", "status": {"key": "open"}}',
            "--condition",
            '{"type": "CommentFullyMatchCondition", "word": "Open"}',
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 16
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "T",
        "actions": [{"type": "Transition", "status": {"key": "open"}}],
        "conditions": [{"type": "CommentFullyMatchCondition", "word": "Open"}],
    }


@responses.activate
def test_triggers_edit_with_version():
    responses.add(
        responses.PATCH,
        f"{BASE}/queues/DESIGN/triggers/16",
        json={"id": 16, "active": False},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "triggers",
            "edit",
            "DESIGN",
            "16",
            "--inactive",
            "--version",
            "1",
        ],
    )
    assert res.exit_code == 0
    assert responses.calls[0].request.params["version"] == "1"  # ty: ignore[unresolved-attribute]
    assert json.loads(responses.calls[0].request.body) == {"active": False}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_triggers_webhook_log():
    responses.add(
        responses.GET,
        f"{BASE}/queues/DEV/triggers/6/webhooks/log",
        json=[{"id": "x", "duration": 235}],
        status=200,
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "triggers", "webhook-log", "DEV", "6", "--limit", "100"],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["duration"] == 235
    assert responses.calls[0].request.params["limit"] == "100"  # ty: ignore[unresolved-attribute]
