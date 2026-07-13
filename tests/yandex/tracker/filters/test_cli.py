"""CLI wiring for `tracker filters` (get)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

runner = CliRunner()


@responses.activate
def test_filters_get():
    responses.add(
        responses.GET,
        f"{BASE}/filters/12345",
        json={"id": 12345, "name": "My open issues", "filter": {"status": "open"}},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "filters", "get", "12345"])
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 12345


@responses.activate
def test_filters_create_parses_filter_json():
    responses.add(
        responses.POST, f"{BASE}/filters/", json={"id": 12345, "name": "My open"}, status=201
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "filters",
            "create",
            "--name",
            "My open",
            "--filter",
            '{"status": "open"}',
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 12345
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": "My open", "filter": {"status": "open"}}


@responses.activate
def test_filters_edit_sends_query_no_version():
    responses.add(
        responses.PATCH, f"{BASE}/filters/12345", json={"id": 12345, "name": "Renamed"}, status=200
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "tracker", "filters", "edit", "12345", "--name", "Renamed"],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["name"] == "Renamed"
    assert "version=" not in responses.calls[0].request.url  # ty: ignore[unsupported-operator]


def test_filters_create_rejects_invalid_json():
    res = runner.invoke(
        cli.app,
        ["tracker", "filters", "create", "--name", "X", "--filter", "not-json"],
    )
    assert res.exit_code != 0


def test_filters_create_rejects_non_object_filter():
    res = runner.invoke(
        cli.app,
        ["tracker", "filters", "create", "--name", "X", "--filter", "[1, 2]"],
    )
    assert res.exit_code != 0
