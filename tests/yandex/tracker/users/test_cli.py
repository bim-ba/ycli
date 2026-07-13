"""TDD for the `tracker users` CLI (passes only once the resource is mounted by the integrator)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

runner = CliRunner()


@responses.activate
def test_users_get():
    responses.add(
        responses.GET,
        f"{BASE}/users/username",
        json={"uid": 12, "login": "username", "display": "Ivan"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "users", "get", "username"])
    assert res.exit_code == 0 and json.loads(res.stdout)["login"] == "username"


@responses.activate
def test_users_list():
    responses.add(
        responses.GET,
        f"{BASE}/users/_relative",
        json={"users": [{"uid": 1, "login": "a"}], "hasNext": False},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "users", "list", "--limit", "1"])
    assert res.exit_code == 0 and json.loads(res.stdout)[0]["login"] == "a"
