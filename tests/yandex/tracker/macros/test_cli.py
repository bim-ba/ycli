"""CLI tests for `tracker macros` (require the resource wired into the root app)."""

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
def test_macros_list():
    responses.add(
        responses.GET, f"{BASE}/queues/TEST/macros", json=[{"id": 3, "name": "a"}], status=200
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "macros", "list", "TEST"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["name"] == "a"


@responses.activate
def test_macros_get():
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST/macros/3",
        json={"id": 3, "name": "My macro"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "macros", "get", "TEST", "3"])
    assert res.exit_code == 0 and json.loads(res.stdout)["name"] == "My macro"


@responses.activate
def test_macros_create():
    responses.add(
        responses.POST, f"{BASE}/queues/TEST/macros", json={"id": 3, "name": "New"}, status=201
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "macros",
            "create",
            "TEST",
            "--name",
            "New",
            "--body",
            "Hi",
            "--issue-update",
            '{"tags": {"add": "x"}}',
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["name"] == "New"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "New",
        "body": "Hi",
        "issueUpdate": {"tags": {"add": "x"}},
    }


@responses.activate
def test_macros_edit():
    responses.add(
        responses.PATCH,
        f"{BASE}/queues/TEST/macros/3",
        json={"id": 3, "name": "Renamed"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "macros", "edit", "TEST", "3", "--name", "Renamed"],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["name"] == "Renamed"
    assert json.loads(responses.calls[0].request.body) == {"name": "Renamed"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_macros_delete():
    responses.add(responses.DELETE, f"{BASE}/queues/TEST/macros/3", status=204)
    res = runner.invoke(cli.app, ["tracker", "macros", "delete", "TEST", "3"])
    assert res.exit_code == 0 and "Deleted macro 3 from queue TEST" in res.stdout
