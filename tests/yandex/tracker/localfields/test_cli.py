"""TDD for the `tracker localfields` CLI (runs after the integrator mounts the resource)."""

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
def test_localfields_list():
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields",
        json=[{"key": "loc_field_key", "name": "Loc field"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "localfields", "list", "ORG"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "loc_field_key"


@responses.activate
def test_localfields_get():
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields/loc_field_key",
        json={"key": "loc_field_key", "name": "loc_field_name", "schema": {"type": "string"}},
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "localfields", "get", "ORG", "loc_field_key"]
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "loc_field_key"
