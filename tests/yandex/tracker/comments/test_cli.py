"""TDD for `tracker comments` CLI."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

pytestmark = pytest.mark.integration

runner = CliRunner()


def _comments_page_callback(request):
    """Two-page drain: page 1 (no id) → id=2 empty page terminates."""
    if "id=" in request.url:
        return (200, {}, json.dumps([]))
    return (200, {}, json.dumps([{"id": 1, "text": "hi"}, {"id": 2, "text": "again"}]))


@responses.activate
def test_list_drains_pages():
    responses.add_callback(
        responses.GET,
        f"{BASE}/issues/DE-1/comments",
        callback=_comments_page_callback,
        content_type="application/json",
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "comments", "list", "DE-1"])
    assert res.exit_code == 0
    assert [c["text"] for c in json.loads(res.stdout)] == ["hi", "again"]
    assert len(responses.calls) == 2  # page 1 + the id=2 empty page


@responses.activate
def test_list_with_limit():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/comments",
        json=[{"id": 1, "text": "hi"}, {"id": 2, "text": "again"}],
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "comments", "list", "DE-1", "--limit", "1"]
    )
    assert res.exit_code == 0
    assert [c["text"] for c in json.loads(res.stdout)] == ["hi"]
    assert len(responses.calls) == 1  # limit satisfied by page 1 — no second fetch


@responses.activate
def test_list_all_is_uncapped():
    responses.add(responses.GET, f"{BASE}/issues/DE-1/comments", json=[], status=200)
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "comments", "list", "DE-1", "--all"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout) == []


@responses.activate
def test_add():
    responses.add(
        responses.POST, f"{BASE}/issues/DE-1/comments/", json={"id": 5, "text": "added"}, status=201
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "comments", "add", "DE-1", "--text", "added"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == 5
    assert json.loads(responses.calls[0].request.body) == {"text": "added"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_edit():
    responses.add(
        responses.PATCH,
        f"{BASE}/issues/DE-1/comments/5",
        json={"id": 5, "text": "fixed"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "comments", "edit", "DE-1", "5", "--text", "fixed"],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["text"] == "fixed"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"text": "fixed"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete():
    responses.add(responses.DELETE, f"{BASE}/issues/DE-1/comments/5", status=204)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "comments", "delete", "DE-1", "5"])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "deleted comment 5 on DE-1"}
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_react():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/comments/5/reactions/LIKE",
        json={"id": 5, "text": "hi"},
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "comments", "react", "DE-1", "5", "LIKE"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == 5
    assert responses.calls[0].request.url.endswith(  # ty: ignore[unresolved-attribute]
        "/reactions/LIKE"
    )
