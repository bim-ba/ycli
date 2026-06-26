"""TDD for `tracker transitions` CLI."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.transitions.cli import app

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


def _stub() -> TrackerClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TrackerClient(session=s)


@responses.activate
def test_list(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1/transitions",
                  json=[{"id": "close", "display": "Close"}], status=200)
    res = runner.invoke(app, ["list", "DE-1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "close"


@responses.activate
def test_execute_with_field(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/DE-1/transitions/close/_execute",
                  json=[{"id": "reopen"}], status=200)
    res = runner.invoke(app, ["execute", "DE-1", "close", "--field", "comment=done"])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == [{"id": "reopen"}]
    assert json.loads(responses.calls[0].request.body) == {"comment": "done"}
