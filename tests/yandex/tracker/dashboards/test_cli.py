"""TDD for `tracker dashboards` CLI (wiring-dependent — run by the integrator after mount)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@responses.activate
def test_create():
    responses.add(
        responses.POST, f"{BASE}/dashboards/", json={"id": 10, "name": "Team board"}, status=201
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "dashboards",
            "create",
            "--name",
            "Team board",
            "--layout",
            "two-columns",
            "--owner",
            "user",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == 10
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Team board",
        "layout": "two-columns",
        "owner": {"id": "user"},
    }


@responses.activate
def test_add_widget_cycletime():
    responses.add(
        responses.POST,
        f"{BASE}/dashboards/10/widgets/cycleTime",
        json={"id": 123456, "description": "My widget"},
        status=201,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "dashboards",
            "add-widget",
            "cycletime",
            "10",
            "--description",
            "My widget",
            "--query",
            "Queue: TEST",
            "--from-status",
            "open",
            "--to-status",
            "closed",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "description": "My widget",
        "query": "Queue: TEST",
        "fromStatuses": [{"key": "open"}],
        "toStatuses": [{"key": "closed"}],
    }
