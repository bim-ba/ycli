"""TDD for `tracker links` CLI."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_list():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/links",
        json=[{"type": {"id": "relates"}, "direction": "outward", "object": {"key": "DE-2"}}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "links", "list", "DE-1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["direction"] == "outward"


@responses.activate
def test_add():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/links",
        json={"id": 7, "type": {"id": "relates"}, "object": {"key": "DE-2"}},
        status=201,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "links", "add", "DE-1", "relates", "DE-2"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == 7
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "relationship": "relates",
        "issue": "DE-2",
    }


def test_add_rejects_bad_relationship():
    res = runner.invoke(cli.app, ["tracker", "links", "add", "DE-1", "bogus", "DE-2"])
    assert res.exit_code != 0  # Enum validation rejects it


@responses.activate
def test_delete():
    responses.add(responses.DELETE, f"{BASE}/issues/DE-1/links/42", status=204)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "links", "delete", "DE-1", "42"])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "deleted link 42 on DE-1"}
    assert responses.calls[0].request.method == "DELETE"
