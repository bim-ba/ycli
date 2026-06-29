"""TDD for `forms me` CLI — dumps the full User model as JSON."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.forms.yandex.net/v1"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


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
