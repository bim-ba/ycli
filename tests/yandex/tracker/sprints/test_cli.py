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
