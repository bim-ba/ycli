"""TDD for `tracker remotelinks` CLI (wiring-dependent — run by the integrator after mount)."""

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
        f"{BASE}/issues/JUNE-2/remotelinks",
        json=[{"id": 51, "object": {"key": "TEST-17"}}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "remotelinks", "list", "JUNE-2"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["id"] == 51


@responses.activate
def test_create():
    responses.add(
        responses.POST,
        f"{BASE}/issues/JUNE-2/remotelinks",
        json={"id": 51, "object": {"key": "TEST-17"}},
        status=201,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "remotelinks",
            "create",
            "JUNE-2",
            "--key",
            "TEST-17",
            "--origin",
            "ru.yandex.bitbucket",
            "--backlink",
        ],
    )
    assert res.exit_code == 0
    assert "backlink=true" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "relationship": "RELATES",
        "key": "TEST-17",
        "origin": "ru.yandex.bitbucket",
    }


@responses.activate
def test_delete():
    responses.add(responses.DELETE, f"{BASE}/issues/JUNE-2/remotelinks/51", status=204)
    res = runner.invoke(
        cli.app, ["--format", "json", "tracker", "remotelinks", "delete", "JUNE-2", "51"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": "deleted remote link 51 on JUNE-2"}
