"""TDD for `tracker comments` CLI."""

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
def test_list():
    responses.add(
        responses.GET, f"{BASE}/issues/DE-1/comments", json=[{"id": 1, "text": "hi"}], status=200
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "comments", "list", "DE-1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["text"] == "hi"


@responses.activate
def test_add():
    responses.add(
        responses.POST, f"{BASE}/issues/DE-1/comments/", json={"id": 5, "text": "added"}, status=201
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "comments", "add", "DE-1", "--text", "added"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == 5
    assert json.loads(responses.calls[0].request.body) == {"text": "added"}  # ty: ignore[invalid-argument-type]
