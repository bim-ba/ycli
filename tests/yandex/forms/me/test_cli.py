"""TDD for `forms me` CLI — dumps the full User model as JSON."""
import json

import requests
import responses
from typer.testing import CliRunner

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.me.cli import app

BASE = "https://api.forms.yandex.net/v1"
runner = CliRunner()


def _stub() -> FormsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return FormsClient(session=s)


@responses.activate
def test_get_dumps_user(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/users/me",
                  json={"id": 1, "uid": "u", "cloud_uid": "c", "email": "e@x"}, status=200)
    res = runner.invoke(app, ["get"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["email"] == "e@x"
