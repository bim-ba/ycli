"""TDD for `tracker changelog` CLI."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.tracker.changelog.cli import app
from ycli.yandex.tracker.client import TrackerClient

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


def _stub() -> TrackerClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TrackerClient(session=s)


@responses.activate
def test_list_with_per_page(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1/changelog",
                  json=[{"id": "ch1", "type": "IssueUpdated", "fields": []}], status=200)
    res = runner.invoke(app, ["list", "DE-1", "--per-page", "50"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "ch1"
    assert responses.calls[0].request.params["perPage"] == "50"
