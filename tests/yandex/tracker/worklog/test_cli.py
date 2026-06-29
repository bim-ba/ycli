"""TDD for `tracker worklog` CLI."""

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
def test_list():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/worklog",
        json=[{"id": 5, "duration": "PT2H"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "worklog", "list", "DE-1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["duration"] == "PT2H"
