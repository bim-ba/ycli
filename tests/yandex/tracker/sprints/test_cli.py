"""CLI tests for `tracker sprints` (require the resource wired into the root app)."""

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
def test_sprints_list():
    responses.add(
        responses.GET,
        f"{BASE}/boards/3/sprints",
        json=[{"id": 4405, "name": "Sprint 1"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "sprints", "list", "3"])
    assert res.exit_code == 0
    assert [s["name"] for s in json.loads(res.stdout)] == ["Sprint 1"]


@responses.activate
def test_sprints_get():
    responses.add(
        responses.GET, f"{BASE}/sprints/4405", json={"id": 4405, "name": "Sprint 1"}, status=200
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "sprints", "get", "4405"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["name"] == "Sprint 1"


@responses.activate
def test_sprints_create():
    responses.add(responses.POST, f"{BASE}/sprints", json={"id": 4405, "name": "New"}, status=201)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "sprints",
            "create",
            "--board-id",
            "1",
            "--name",
            "New Sprint",
            "--start-date",
            "2018-10-21",
            "--end-date",
            "2018-10-24",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body)["board"] == {"id": "1"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_sprints_edit():
    responses.add(
        responses.PATCH, f"{BASE}/sprints/4405", json={"id": 4405, "name": "Updated"}, status=200
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "sprints", "edit", "4405", "--name", "Updated"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["name"] == "Updated"


@responses.activate
def test_sprints_delete():
    responses.add(responses.DELETE, f"{BASE}/sprints/4405", status=204)
    res = runner.invoke(cli.app, ["tracker", "sprints", "delete", "4405"])
    assert res.exit_code == 0
    assert "Deleted sprint 4405" in res.stdout


@responses.activate
def test_sprints_start():
    responses.add(
        responses.POST,
        f"{BASE}/sprints/4405/_start",
        json={"id": 4405, "status": "in_progress"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "sprints", "start", "4405"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["status"] == "in_progress"


@responses.activate
def test_sprints_archive():
    responses.add(
        responses.POST,
        f"{BASE}/sprints/4405/_archive",
        json={"id": 4405, "status": "archived"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "sprints", "archive", "4405"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["status"] == "archived"
