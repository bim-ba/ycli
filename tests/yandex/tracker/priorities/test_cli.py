"""TDD for the three Tracker lookup CLIs (priorities/issuetypes/linktypes)."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issuetypes.cli import app as issuetypes_app
from ycli.yandex.tracker.linktypes.cli import app as linktypes_app
from ycli.yandex.tracker.priorities.cli import app as priorities_app

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


def _stub() -> TrackerClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TrackerClient(session=s)


@responses.activate
def test_priorities_list(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/priorities", json=[{"key": "critical", "display": "Critical"}], status=200)
    res = runner.invoke(priorities_app, ["list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "critical"


@responses.activate
def test_issuetypes_list(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issuetypes", json=[{"key": "task", "display": "Task"}], status=200)
    res = runner.invoke(issuetypes_app, ["list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "task"


@responses.activate
def test_linktypes_list(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/linktypes", json=[{"id": "relates"}], status=200)
    res = runner.invoke(linktypes_app, ["list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "relates"
