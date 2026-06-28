"""TDD for `forms surveys` CLI — list dumps flat SurveyCollection; get dumps one survey."""
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
def test_list_dumps_flat_collection():
    responses.add(responses.GET, f"{BASE}/surveys",
                  json={"links": {}, "result": [{"id": "a", "name": "A"}]}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "forms", "surveys", "list"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["id"] == "a"


@responses.activate
def test_get_dumps_survey():
    responses.add(responses.GET, f"{BASE}/surveys/{SID}",
                  json={"id": SID, "name": "F", "is_published": True}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "forms", "surveys", "get", SID])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["id"] == SID and out["is_published"] is True
