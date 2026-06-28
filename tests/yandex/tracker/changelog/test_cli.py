"""TDD for `tracker changelog` CLI."""

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
def test_list_with_per_page():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/changelog",
        json=[{"id": "ch1", "type": "IssueUpdated", "fields": []}],
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "changelog", "list", "DE-1", "--per-page", "50"]
    )
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "ch1"
    assert responses.calls[0].request.params["perPage"] == "50"
