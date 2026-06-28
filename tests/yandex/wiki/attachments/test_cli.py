"""TDD for `wiki attachments` CLI."""

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
def test_attachments_list():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "f.pdf", "size": 0, "mime_type": "application/pdf"}]},
        status=200,
    )
    result = runner.invoke(cli.app, ["wiki", "attachments", "list", "42"])
    assert result.exit_code == 0 and "f.pdf" in result.stdout
