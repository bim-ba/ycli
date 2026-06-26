"""TDD for `forms answers` CLI — dumps the {columns, answers, next} envelope."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.forms.answers.cli import app
from ycli.yandex.forms.client import FormsClient

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
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/answers",
                  json={"columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
                        "answers": [{"id": 99, "created": "2026-01-01", "data": [{"value": "x"}]}],
                        "next": None}, status=200)
    res = runner.invoke(app, ["list", SID])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["answers"][0]["id"] == 99 and out["next"] is None
