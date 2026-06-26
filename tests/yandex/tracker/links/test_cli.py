"""TDD for `tracker links` CLI."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.links.cli import app

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


def _stub() -> TrackerClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TrackerClient(session=s)


@responses.activate
def test_list(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1/links",
                  json=[{"type": {"id": "relates"}, "direction": "outward", "object": {"key": "DE-2"}}], status=200)
    res = runner.invoke(app, ["list", "DE-1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["direction"] == "outward"


@responses.activate
def test_add(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/DE-1/links",
                  json={"id": 7, "type": {"id": "relates"}, "object": {"key": "DE-2"}}, status=201)
    res = runner.invoke(app, ["add", "DE-1", "relates", "DE-2"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == 7
    assert json.loads(responses.calls[0].request.body) == {"relationship": "relates", "issue": "DE-2"}


def test_add_rejects_bad_relationship(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    res = runner.invoke(app, ["add", "DE-1", "bogus", "DE-2"])
    assert res.exit_code != 0  # Enum validation rejects it
