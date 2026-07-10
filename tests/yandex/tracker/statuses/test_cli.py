"""TDD for the `tracker statuses` CLI (list + create + edit)."""

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


@responses.activate
def test_statuses_create():
    responses.add(responses.POST, f"{BASE}/statuses/", json={"id": 1, "key": "pause"}, status=201)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "statuses",
            "create",
            "--key",
            "pause",
            "--name-ru",
            "Пауза",
            "--type",
            "paused",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "pause"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"key": "pause", "name": {"ru": "Пауза"}, "type": "paused"}


@responses.activate
def test_statuses_edit_sends_version():
    responses.add(
        responses.PATCH, f"{BASE}/statuses/29", json={"id": 29, "key": "pause"}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "statuses",
            "edit",
            "29",
            "--name-ru",
            "Приостановлен",
            "--version",
            "1",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 29
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
