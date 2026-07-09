"""TDD for `wiki comments` CLI."""

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.wiki.yandex.net/v1"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_comments_list():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={"results": [{"content": "hi"}]},
        status=200,
    )
    result = runner.invoke(cli.app, ["wiki", "comments", "list", "42"])
    assert result.exit_code == 0 and "hi" in result.stdout


@responses.activate
def test_comments_thread():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments/7/thread",
        json={"results": [{"content": "reply"}], "next_cursor": None},
        status=200,
    )
    result = runner.invoke(cli.app, ["wiki", "comments", "thread", "42", "7"])
    assert result.exit_code == 0 and "reply" in result.stdout
