"""CLI wiring for `tracker applications` (list)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@responses.activate
def test_applications_list():
    responses.add(
        responses.GET,
        f"{BASE}/applications",
        json=[{"id": "my-application", "type": "my-application", "name": "Application name"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "applications", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["id"] == "my-application"
