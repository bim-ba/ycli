"""TDD for the `tracker resolutions` CLI (list + create + edit)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

runner = CliRunner()


@responses.activate
def test_resolutions_list():
    responses.add(
        responses.GET,
        f"{BASE}/resolutions",
        json=[{"id": 1, "key": "fixed", "name": "Решен"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "resolutions", "list"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["key"] == "fixed"


@responses.activate
def test_resolutions_create():
    responses.add(
        responses.POST, f"{BASE}/resolutions/", json={"id": 9, "key": "wontFix"}, status=201
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "resolutions",
            "create",
            "--key",
            "wontFix",
            "--name-ru",
            "Отклонено",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "wontFix"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"key": "wontFix", "name": {"ru": "Отклонено"}}


@responses.activate
def test_resolutions_edit_sends_version():
    responses.add(
        responses.PATCH, f"{BASE}/resolutions/9", json={"id": 9, "key": "wontFix"}, status=200
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "resolutions",
            "edit",
            "9",
            "--description",
            "Won't be fixed",
            "--version",
            "1",
        ],
    )
    assert res.exit_code == 0 and json.loads(res.stdout)["id"] == 9
    assert "version=1" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
