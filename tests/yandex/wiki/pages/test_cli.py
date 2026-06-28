"""TDD for `wiki pages` CLI."""
import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli as cli

BASE = "https://api.wiki.yandex.net/v1"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_pages_get_prints_body():
    responses.add(responses.GET, f"{BASE}/pages",
                  json={"id": 1, "slug": "data/x", "title": "T", "content": "# B"}, status=200)
    result = runner.invoke(cli.app, ["wiki", "pages", "get", "data/x"])
    assert result.exit_code == 0
    assert "# B" in result.stdout


@responses.activate
def test_pages_create_dumps_model_json():
    responses.add(responses.POST, f"{BASE}/pages",
                  json={"id": 7, "slug": "data/x", "title": "T"}, status=200)
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "pages", "create", "--slug", "data/x", "--title", "T", "--content", "# B"])
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["id"] == 7 and out["slug"] == "data/x"
    sent = json.loads(responses.calls[0].request.body)
    assert sent == {"slug": "data/x", "title": "T", "content": "# B"}


@responses.activate
def test_pages_descendants_dumps_model_json():
    responses.add(responses.GET, f"{BASE}/pages/descendants",
                  json={"results": [{"id": 2, "slug": "data/x/child"}], "next_cursor": None}, status=200)
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "pages", "descendants", "data/x", "--limit", "50"])
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["results"][0]["slug"] == "data/x/child"
    assert out["next_cursor"] is None
    req = responses.calls[-1].request
    assert req.params["slug"] == "data/x"
    assert req.params["page_size"] == "50"


@responses.activate
def test_pages_update_dumps_model_json():
    responses.add(responses.POST, f"{BASE}/pages/77",
                  json={"id": 77, "slug": "data/x", "title": "New"}, status=200)
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "pages", "update", "77", "--content", "# U", "--title", "New"])
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["id"] == 77 and out["title"] == "New"
    sent = json.loads(responses.calls[0].request.body)
    assert sent == {"content": "# U", "title": "New"}


def test_pages_subcommand_help_needs_no_creds(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    result = runner.invoke(cli.app, ["wiki", "pages", "get", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout or "usage" in result.stdout.lower()
