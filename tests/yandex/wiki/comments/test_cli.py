"""TDD for `wiki comments` CLI."""

import json

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
    """`thread` reconstructs from the flat comments list (the /thread endpoint is dead)."""
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={
            "results": [
                {"id": 7, "body": "root", "parent_id": None},
                {"id": 8, "body": "reply", "parent_id": 7},
            ]
        },
        status=200,
    )
    result = runner.invoke(cli.app, ["wiki", "comments", "thread", "42", "7"])
    assert result.exit_code == 0 and "reply" in result.stdout


@responses.activate
def test_comments_create_posts_typed_body():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/comments",
        json={"id": 99, "body": "LGTM"},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "comments",
            "create",
            "42",
            "--body",
            "LGTM",
            "--parent-id",
            "7",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["id"] == 99
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"body": "LGTM", "parent_id": 7}


@responses.activate
def test_comments_delete_emits_comments_count():
    responses.add(
        responses.DELETE, f"{BASE}/pages/42/comments/7", json={"comments_count": 4}, status=200
    )
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "comments", "delete", "42", "7"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["comments_count"] == 4
    assert responses.calls[0].request.method == "DELETE"
