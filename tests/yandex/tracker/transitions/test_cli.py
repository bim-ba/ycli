"""TDD for `tracker transitions` CLI."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

pytestmark = pytest.mark.integration

runner = CliRunner()


@responses.activate
def test_list():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/transitions",
        json=[{"id": "close", "display": "Close"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "transitions", "list", "DE-1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "close"


@responses.activate
def test_execute_with_field():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/transitions/close/_execute",
        json=[
            {
                "self": "https://api.tracker.yandex.net/v3/issues/DE-1/transitions/close",
                "id": "close",
                "to": {"id": "3", "key": "closed", "display": "Closed"},
                "screen": {"id": "scr1"},
            }
        ],
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "transitions",
            "execute",
            "DE-1",
            "close",
            "--field",
            "comment=done",
        ],
    )
    assert res.exit_code == 0
    parsed = json.loads(res.stdout)
    assert parsed[0]["id"] == "close"
    assert parsed[0]["to"]["key"] == "closed"
    assert parsed[0]["to"]["display"] == "Closed"
    assert json.loads(responses.calls[0].request.body) == {"comment": "done"}  # ty: ignore[invalid-argument-type]
