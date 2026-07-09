"""CLI wiring for `tracker components` (list)."""

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
def test_components_list():
    responses.add(
        responses.GET,
        f"{BASE}/components",
        json=[{"id": 1, "name": "Test", "queue": {"key": "ORG", "display": "My queue"}}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "components", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["name"] == "Test"


@responses.activate
def test_components_create():
    responses.add(
        responses.POST, f"{BASE}/components", json={"id": 111175, "name": "UI"}, status=201
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "components",
            "create",
            "--name",
            "UI",
            "--queue",
            "TEST",
            "--assign-auto",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 111175
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": "UI", "queue": "TEST", "assignAuto": True}


@responses.activate
def test_components_edit_sends_version():
    responses.add(
        responses.PATCH, f"{BASE}/components/111175", json={"id": 111175, "name": "UI"}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "components",
            "edit",
            "111175",
            "--name",
            "New UI",
            "--version",
            "1",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 111175
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
