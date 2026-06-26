"""TDD for `forms questions` CLI — dumps the {pages} envelope."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.questions.cli import app

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"
runner = CliRunner()


def _stub() -> FormsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return FormsClient(session=s)


@responses.activate
def test_list_dumps_pages_envelope(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/questions",
                  json={"pages": [{"id": 1, "items": [{"id": 11, "slug": "s1", "type": "string", "label": "A"}]}]},
                  status=200)
    res = runner.invoke(app, ["list", SID])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["pages"][0]["items"][0]["id"] == 11
