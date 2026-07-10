"""TDD for `tracker worklog` CLI."""

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
        f"{BASE}/issues/DE-1/worklog",
        json=[{"id": 5, "duration": "PT2H"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "worklog", "list", "DE-1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["duration"] == "PT2H"


@responses.activate
def test_add():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/worklog",
        json={"id": 1, "duration": "PT2H"},
        status=201,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "worklog",
            "add",
            "DE-1",
            "--duration",
            "PT2H",
            "--comment",
            "did work",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["duration"] == "PT2H"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "duration": "PT2H",
        "comment": "did work",
    }


@responses.activate
def test_edit():
    responses.add(
        responses.PATCH,
        f"{BASE}/issues/DE-1/worklog/1",
        json={"id": 1, "duration": "PT30M"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "worklog", "edit", "DE-1", "1", "--duration", "PT30M"],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["duration"] == "PT30M"
    assert json.loads(responses.calls[0].request.body) == {"duration": "PT30M"}  # ty: ignore[invalid-argument-type]


@responses.activate
def test_delete():
    responses.add(responses.DELETE, f"{BASE}/issues/DE-1/worklog/1", status=204)
    res = runner.invoke(cli.app, ["tracker", "worklog", "delete", "DE-1", "1"])
    assert res.exit_code == 0
    assert "Deleted worklog 1 on DE-1" in res.stdout
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_search():
    responses.add(
        responses.POST, f"{BASE}/worklog/_search", json=[{"id": 1, "duration": "PT2H"}], status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "worklog",
            "search",
            "--created-by",
            "veikus",
            "--from",
            "2018-06-06",
            "--to",
            "2018-06-07",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["duration"] == "PT2H"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "createdBy": "veikus",
        "createdAt": {"from": "2018-06-06", "to": "2018-06-07"},
    }


@responses.activate
def test_global_list():
    responses.add(responses.GET, f"{BASE}/worklog", json=[{"id": 1, "duration": "P3W"}], status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "worklog",
            "global-list",
            "--created-by",
            "veikus",
            "--from",
            "2018-06-06",
            "--to",
            "2018-06-07",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["duration"] == "P3W"
    url = responses.calls[0].request.url
    assert "createdBy=veikus" in url and "createdAt=from" in url  # ty: ignore[unsupported-operator]
