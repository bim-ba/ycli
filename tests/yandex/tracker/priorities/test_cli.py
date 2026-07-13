"""TDD for the three Tracker lookup CLIs (priorities/issuetypes/linktypes)."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

pytestmark = pytest.mark.integration

runner = CliRunner()


@responses.activate
def test_priorities_list():
    responses.add(
        responses.GET,
        f"{BASE}/priorities",
        json=[{"key": "critical", "display": "Critical"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "priorities", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "critical"


@responses.activate
def test_issuetypes_list():
    responses.add(
        responses.GET, f"{BASE}/issuetypes", json=[{"key": "task", "display": "Task"}], status=200
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "issuetypes", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "task"


@responses.activate
def test_linktypes_list():
    responses.add(responses.GET, f"{BASE}/linktypes", json=[{"id": "relates"}], status=200)
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "linktypes", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "relates"


@responses.activate
def test_priorities_create():
    responses.add(responses.POST, f"{BASE}/priorities/", json={"id": 6, "key": "one"}, status=201)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "priorities",
            "create",
            "--key",
            "one",
            "--name-ru",
            "Низкий",
            "--order",
            "60",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "one"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"key": "one", "name": {"ru": "Низкий"}, "order": 60}


@responses.activate
def test_priorities_edit_sends_version():
    responses.add(
        responses.PATCH, f"{BASE}/priorities/one", json={"id": 6, "key": "one"}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "priorities",
            "edit",
            "one",
            "--name-ru",
            "Низкий",
            "--version",
            "1",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "one"
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
