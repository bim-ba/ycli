import json
import requests
import responses
from typer.testing import CliRunner
from ycli.yandex.wiki.cli import app
from ycli.yandex.wiki.client import WikiClient

BASE = "https://api.wiki.yandex.net/v1"
runner = CliRunner()


def _stub_root() -> WikiClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return WikiClient(session=s)


@responses.activate
def test_pages_get_prints_body(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub_root()))
    responses.add(responses.GET, f"{BASE}/pages",
                  json={"id": 1, "slug": "data/x", "title": "T", "content": "# B"}, status=200)
    result = runner.invoke(app, ["pages", "get", "data/x"])
    assert result.exit_code == 0
    assert "# B" in result.stdout


@responses.activate
def test_pages_create_dumps_model_json(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub_root()))
    responses.add(responses.POST, f"{BASE}/pages",
                  json={"id": 7, "slug": "data/x", "title": "T"}, status=200)
    result = runner.invoke(app, ["pages", "create", "--slug", "data/x", "--title", "T", "--content", "# B"])
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["id"] == 7 and out["slug"] == "data/x"
    sent = json.loads(responses.calls[0].request.body)
    assert sent == {"slug": "data/x", "title": "T", "content": "# B"}


@responses.activate
def test_pages_descendants_dumps_model_json(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub_root()))
    responses.add(responses.GET, f"{BASE}/pages/descendants",
                  json={"results": [{"id": 2, "slug": "data/x/child"}], "next_cursor": None}, status=200)
    result = runner.invoke(app, ["pages", "descendants", "data/x", "--limit", "50"])
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["results"][0]["slug"] == "data/x/child"
    assert out["next_cursor"] is None  # null must round-trip (pagination contract)
    req = responses.calls[-1].request
    assert req.params["slug"] == "data/x"  # slug threaded into the query
    assert req.params["page_size"] == "50"  # --limit mapped to page_size


@responses.activate
def test_pages_update_dumps_model_json(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub_root()))
    responses.add(responses.POST, f"{BASE}/pages/77",
                  json={"id": 77, "slug": "data/x", "title": "New"}, status=200)
    result = runner.invoke(app, ["pages", "update", "77", "--content", "# U", "--title", "New"])
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["id"] == 77 and out["title"] == "New"
    sent = json.loads(responses.calls[0].request.body)
    assert sent == {"content": "# U", "title": "New"}


def test_pages_subcommand_help_needs_no_creds(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    result = runner.invoke(app, ["pages", "get", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout or "usage" in result.stdout.lower()
