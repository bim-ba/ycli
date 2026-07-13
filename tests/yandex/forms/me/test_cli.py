"""TDD for `forms me` CLI — dumps the full User model as JSON."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import FORMS_BASE as BASE

runner = CliRunner()


@responses.activate
def test_get_dumps_user():
    responses.add(
        responses.GET,
        f"{BASE}/users/me",
        json={"id": 1, "uid": "u", "cloud_uid": "c", "email": "e@x"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "me", "get"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["email"] == "e@x"
