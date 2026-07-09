"""TDD for the `tracker statuses` CLI (passes only once the integrator mounts the resource)."""

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
def test_statuses_list():
    responses.add(
        responses.GET,
        f"{BASE}/statuses",
        json=[{"id": 1, "key": "open", "type": "new"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "statuses", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "open"
