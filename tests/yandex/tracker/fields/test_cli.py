"""CLI wiring for `tracker fields` (list + get)."""

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
def test_fields_list():
    responses.add(
        responses.GET,
        f"{BASE}/fields",
        json=[{"id": "ruName", "key": "ruName", "schema": {"type": "string"}}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "fields", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "ruName"


@responses.activate
def test_fields_get():
    responses.add(
        responses.GET,
        f"{BASE}/fields/ruName",
        json={"id": "ruName", "name": "Field"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "fields", "get", "ruName"])
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == "ruName"
