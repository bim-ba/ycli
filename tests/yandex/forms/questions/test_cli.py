"""TDD for `forms questions` CLI — dumps the {pages} envelope."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli as cli

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_list_dumps_pages_envelope():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/questions",
        json={
            "pages": [
                {"id": 1, "items": [{"id": 11, "slug": "s1", "type": "string", "label": "A"}]}
            ]
        },
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "questions", "list", SID])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["pages"][0]["items"][0]["id"] == 11
