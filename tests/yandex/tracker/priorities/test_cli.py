"""TDD for the three Tracker lookup CLIs (priorities/issuetypes/linktypes)."""
import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_priorities_list():
    responses.add(responses.GET, f"{BASE}/priorities", json=[{"key": "critical", "display": "Critical"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "priorities", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "critical"


@responses.activate
def test_issuetypes_list():
    responses.add(responses.GET, f"{BASE}/issuetypes", json=[{"key": "task", "display": "Task"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "issuetypes", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "task"


@responses.activate
def test_linktypes_list():
    responses.add(responses.GET, f"{BASE}/linktypes", json=[{"id": "relates"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "linktypes", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "relates"
