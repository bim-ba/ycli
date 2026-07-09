"""TDD for the `tracker queues` CLI (runs after the integrator mounts the resource)."""

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
def test_queues_list():
    responses.add(responses.GET, f"{BASE}/queues/", json=[{"id": "3", "key": "TEST"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "TEST"


@responses.activate
def test_queues_list_all_flag():
    responses.add(responses.GET, f"{BASE}/queues/", json=[{"key": "TEST"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "list", "--all"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "TEST"


@responses.activate
def test_queues_get_with_expand():
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST",
        json={"id": "3", "key": "TEST", "name": "Test"},
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "queues", "get", "TEST", "--expand", "all"]
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "TEST"
    assert responses.calls[0].request.params["expand"] == "all"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_queues_get_without_expand():
    responses.add(responses.GET, f"{BASE}/queues/TEST", json={"id": "3", "key": "TEST"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "queues", "get", "TEST"])
    assert res.exit_code == 0
    assert "expand" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]
