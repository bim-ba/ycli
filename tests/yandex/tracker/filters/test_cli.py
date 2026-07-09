"""CLI wiring for `tracker filters` (get)."""

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
def test_filters_get():
    responses.add(
        responses.GET,
        f"{BASE}/filters/12345",
        json={"id": 12345, "name": "My open issues", "filter": {"status": "open"}},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "filters", "get", "12345"])
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 12345
