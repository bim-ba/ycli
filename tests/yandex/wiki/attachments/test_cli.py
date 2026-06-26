import requests
import responses
from typer.testing import CliRunner
from ycli.yandex.wiki.cli import app
from ycli.yandex.wiki.client import WikiClient

BASE = "https://api.wiki.yandex.net/v1"
runner = CliRunner()


def _stub():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return WikiClient(session=s)


@responses.activate
def test_attachments_list(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/pages/42/attachments",
                  json={"results": [{"name": "f.pdf", "size": 0, "mime_type": "application/pdf"}]}, status=200)
    result = runner.invoke(app, ["attachments", "list", "42"])
    assert result.exit_code == 0 and "f.pdf" in result.stdout
