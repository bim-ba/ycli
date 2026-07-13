"""CLI tests for `tracker boards` (require the resource wired into the root app)."""

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
def test_boards_get():
    responses.add(responses.GET, f"{BASE}/boards/1", json={"id": 1, "name": "My board"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "boards", "get", "1"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["name"] == "My board"


@responses.activate
def test_boards_list_with_limit():
    responses.add(
        responses.GET,
        f"{BASE}/boards/_paginate",
        json=[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "boards", "list", "--limit", "1"])
    assert res.exit_code == 0
    assert [b["name"] for b in json.loads(res.stdout)] == ["A"]


@responses.activate
def test_boards_list_negative_limit_rejected():
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "boards", "list", "--limit", "-5"])
    assert res.exit_code != 0


@responses.activate
def test_boards_list_all_is_uncapped():
    responses.add(responses.GET, f"{BASE}/boards/_paginate", json=[], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "boards", "list", "--all"])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == []


@responses.activate
def test_boards_create():
    responses.add(
        responses.POST, f"{BASE}/liveBoards/", json={"id": 1, "name": "Testing"}, status=201
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "boards", "create", "--name", "Testing", "--sprints"],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["name"] == "Testing"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Testing",
        "sprintsAvailable": True,
    }


@responses.activate
def test_boards_edit():
    responses.add(
        responses.PATCH, f"{BASE}/boards/5", json={"id": 5, "name": "New name"}, status=200
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "boards", "edit", "5", "--name", "New name"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["name"] == "New name"


@responses.activate
def test_boards_delete():
    responses.add(responses.DELETE, f"{BASE}/boards/5", status=204)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "boards", "delete", "5"])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "deleted board 5"}
