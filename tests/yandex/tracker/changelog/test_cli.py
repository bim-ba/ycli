"""TDD for `tracker changelog` CLI."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

pytestmark = pytest.mark.integration

runner = CliRunner()


def _changelog_page_callback(request):
    """Two-page drain: page 1 (no id) → id=ch2 empty page terminates."""
    if "id=" in request.url:
        return (200, {}, json.dumps([]))
    body = [
        {"id": "ch1", "type": "IssueUpdated", "fields": []},
        {"id": "ch2", "type": "IssueCommentAdded", "fields": []},
    ]
    return (200, {}, json.dumps(body))


@responses.activate
def test_list_drains_pages():
    responses.add_callback(
        responses.GET,
        f"{BASE}/issues/DE-1/changelog",
        callback=_changelog_page_callback,
        content_type="application/json",
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "changelog", "list", "DE-1"])
    assert res.exit_code == 0
    assert [e["id"] for e in json.loads(res.stdout)] == ["ch1", "ch2"]
    assert len(responses.calls) == 2  # page 1 + the id=ch2 empty page
    assert responses.calls[0].request.params["perPage"] == "100"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_with_limit():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/changelog",
        json=[{"id": "ch1", "fields": []}, {"id": "ch2", "fields": []}],
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "changelog", "list", "DE-1", "--limit", "1"]
    )
    assert res.exit_code == 0
    assert [e["id"] for e in json.loads(res.stdout)] == ["ch1"]
    assert len(responses.calls) == 1  # limit satisfied by page 1 — no second fetch


@responses.activate
def test_list_all_is_uncapped():
    responses.add(responses.GET, f"{BASE}/issues/DE-1/changelog", json=[], status=200)
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "changelog", "list", "DE-1", "--all"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout) == []
