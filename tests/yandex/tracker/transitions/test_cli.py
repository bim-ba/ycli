"""TDD for `tracker transitions` CLI."""
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
    responses.add(responses.GET, f"{BASE}/issues/DE-1/transitions",
                  json=[{"id": "close", "display": "Close"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "transitions", "list", "DE-1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "close"


@responses.activate
def test_execute_with_field():
    responses.add(responses.POST, f"{BASE}/issues/DE-1/transitions/close/_execute",
                  json=[{"id": "reopen"}], status=200)
    res = runner.invoke(cli.app, ["tracker", "transitions", "execute", "DE-1", "close", "--field", "comment=done"])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == [{"id": "reopen"}]
    assert json.loads(responses.calls[0].request.body) == {"comment": "done"}
