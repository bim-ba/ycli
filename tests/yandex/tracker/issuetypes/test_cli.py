"""TDD for the `tracker issuetypes` CLI (list + create + edit)."""

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
def test_issuetypes_list():
    responses.add(
        responses.GET, f"{BASE}/issuetypes", json=[{"key": "task", "display": "Task"}], status=200
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "issuetypes", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "task"


@responses.activate
def test_issuetypes_create():
    responses.add(
        responses.POST, f"{BASE}/issuetypes/", json={"id": 23, "key": "client"}, status=201
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "issuetypes",
            "create",
            "--key",
            "client",
            "--name-ru",
            "Клиент",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "client"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"key": "client", "name": {"ru": "Клиент"}}


@responses.activate
def test_issuetypes_edit_sends_version():
    responses.add(
        responses.PATCH, f"{BASE}/issuetypes/23", json={"id": 23, "key": "client"}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "issuetypes",
            "edit",
            "23",
            "--name-ru",
            "Покупатель",
            "--version",
            "1",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "client"
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
