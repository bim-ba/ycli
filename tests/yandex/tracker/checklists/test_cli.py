"""TDD for `tracker checklists` CLI.

NOTE: these invoke the ROOT app (``cli.app``), so they pass only AFTER the orchestrator mounts
``checklists_app`` in ``tracker/cli.py``. The integrator runs them; producer self-validation is
test_client.py + test_models.py (+ the read-only MCP registration check).
"""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@responses.activate
def test_get():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/checklistItems",
        json=[{"id": "5f", "text": "step 1", "checked": False}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "checklists", "get", "DE-1"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["text"] == "step 1"


@responses.activate
def test_add():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/checklistItems",
        json={"key": "DE-1", "checklistItems": [{"id": "5f", "text": "step 1"}]},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "checklists",
            "add",
            "DE-1",
            "--text",
            "step 1",
            "--checked",
            "--assignee",
            "sava",
            "--deadline",
            "2021-05-09T00:00:00.000+0000",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["key"] == "DE-1"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "text": "step 1",
        "checked": True,
        "assignee": "sava",
        "deadline": {"date": "2021-05-09T00:00:00.000+0000", "deadlineType": "date"},
    }


@responses.activate
def test_edit():
    responses.add(
        responses.PATCH,
        f"{BASE}/issues/DE-1/checklistItems/5f",
        json={"key": "DE-1", "checklistItems": [{"id": "5f", "checked": True}]},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "checklists", "edit", "DE-1", "5f", "--checked"],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {"checked": True}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete():
    responses.add(
        responses.DELETE,
        f"{BASE}/issues/DE-1/checklistItems/5f",
        json={"key": "DE-1", "checklistTotal": 0},
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "checklists", "delete", "DE-1", "5f"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["checklistTotal"] == 0
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_clear():
    responses.add(
        responses.DELETE, f"{BASE}/issues/DE-1/checklistItems", json={"key": "DE-1"}, status=200
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "checklists", "clear", "DE-1"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["key"] == "DE-1"
    assert responses.calls[0].request.url.endswith(  # ty: ignore[unresolved-attribute]
        "/checklistItems"
    )
