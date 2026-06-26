"""TDD for `tracker worklog` CLI."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.worklog.cli import app

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


def _stub() -> TrackerClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TrackerClient(session=s)


@responses.activate
def test_list(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1/worklog",
                  json=[{"id": 5, "duration": "PT2H"}], status=200)
    res = runner.invoke(app, ["list", "DE-1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["duration"] == "PT2H"
