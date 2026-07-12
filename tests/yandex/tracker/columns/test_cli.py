"""CLI tests for `tracker columns` (require the resource wired into the root app)."""

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
def test_columns_list():
    responses.add(
        responses.GET,
        f"{BASE}/boards/73/columns",
        json=[{"id": 1, "name": "Open"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "columns", "list", "73"])
    assert res.exit_code == 0
    assert [c["name"] for c in json.loads(res.stdout)] == ["Open"]


@responses.activate
def test_columns_get():
    responses.add(
        responses.GET, f"{BASE}/boards/73/columns/1", json={"id": 1, "name": "Open"}, status=200
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "columns", "get", "73", "1"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["name"] == "Open"


@responses.activate
def test_columns_create():
    responses.add(
        responses.POST, f"{BASE}/boards/73/columns/", json={"id": 5, "name": "Approve"}, status=201
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "columns",
            "create",
            "73",
            "--name",
            "Approve",
            "--status",
            "needInfo",
            "--status",
            "adjustment",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Approve",
        "statuses": ["needInfo", "adjustment"],
    }


@responses.activate
def test_columns_edit():
    responses.add(
        responses.PATCH, f"{BASE}/boards/73/columns/5", json={"id": 5, "name": "Pause"}, status=200
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "columns", "edit", "73", "5", "--name", "Pause"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["name"] == "Pause"


@responses.activate
def test_columns_delete():
    responses.add(responses.DELETE, f"{BASE}/boards/73/columns/5", status=204)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "columns", "delete", "73", "5"])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "deleted column 5 on board 73"}
