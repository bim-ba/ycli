"""TDD for `forms surveys` CLI — list dumps the envelope; get dumps one survey."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.surveys.cli import app

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"
runner = CliRunner()


def _stub() -> FormsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return FormsClient(session=s)


@responses.activate
def test_list_dumps_envelope(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/surveys",
                  json={"links": {}, "result": [{"id": "a", "name": "A"}]}, status=200)
    res = runner.invoke(app, ["list"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["result"][0]["id"] == "a"


@responses.activate
def test_get_dumps_survey(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/surveys/{SID}",
                  json={"id": SID, "name": "F", "is_published": True}, status=200)
    res = runner.invoke(app, ["get", SID])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["id"] == SID and out["is_published"] is True
