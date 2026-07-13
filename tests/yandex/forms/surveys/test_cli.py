"""TDD for `forms surveys` CLI — list dumps flat SurveyList; get dumps one survey."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"
runner = CliRunner()


@responses.activate
def test_list_dumps_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/surveys",
        json={"links": {}, "result": [{"id": "a", "name": "A"}]},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "surveys", "list"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["id"] == "a"


@responses.activate
def test_get_dumps_survey():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}",
        json={"id": SID, "name": "F", "is_published": True},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "surveys", "get", SID])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["id"] == SID and out["is_published"] is True


@responses.activate
def test_create_sends_typed_body_plus_field_escape():
    responses.add(responses.POST, f"{BASE}/surveys", json={"id": SID, "name": "New"}, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "surveys",
            "create",
            "--name",
            "New",
            "--need-auth",
            "--max-count",
            "50",
            "-F",
            "language=ru",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == SID
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"name": "New", "need_auth": True, "max_count": 50, "language": "ru"}


@responses.activate
def test_modify_sends_only_supplied_fields():
    responses.add(
        responses.PATCH, f"{BASE}/surveys/{SID}", json={"id": SID, "name": "Renamed"}, status=200
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "forms", "surveys", "modify", SID, "--name", "Renamed"]
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Renamed",
    }


def test_field_without_equals_is_rejected():
    res = runner.invoke(
        cli.app,
        ["forms", "surveys", "create", "--name", "New", "-F", "brokenfield"],
    )
    assert res.exit_code == 2  # typer.BadParameter from _parse_fields (no '=')


@responses.activate
def test_delete_survey():
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}", status=204)
    res = runner.invoke(cli.app, ["--format", "json", "forms", "surveys", "delete", SID])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": f"deleted survey {SID}"}


@responses.activate
def test_publish_survey():
    responses.add(responses.POST, f"{BASE}/surveys/{SID}/publish", body="OK", status=200)
    res = runner.invoke(cli.app, ["--format", "json", "forms", "surveys", "publish", SID])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": f"published survey {SID}"}


@responses.activate
def test_unpublish_survey():
    responses.add(responses.POST, f"{BASE}/surveys/{SID}/unpublish", body="OK", status=200)
    res = runner.invoke(cli.app, ["--format", "json", "forms", "surveys", "unpublish", SID])
    assert res.exit_code == 0
    assert json.loads(res.stdout) == {"ok": True, "detail": f"unpublished survey {SID}"}
