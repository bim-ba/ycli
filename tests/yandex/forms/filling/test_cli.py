"""TDD for `forms filling` CLI — get / submit / suggest (needs the resource mounted)."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import FORMS_BASE as BASE

pytestmark = pytest.mark.integration

SID = "6818ceffe010db4f59d11329"
runner = CliRunner()


@responses.activate
def test_get():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/form",
        json={"id": SID, "name": "Feedback", "pages": []},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "filling", "get", SID])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["name"] == "Feedback"


@responses.activate
def test_submit_from_body_file(tmp_path):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/form",
        json={"id": SID, "answer_id": 99},
        status=200,
    )
    body_file = tmp_path / "answers.json"
    body_file.write_text(json.dumps({"answer_short_text_1": "Ann"}), encoding="utf-8")
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "filling",
            "submit",
            SID,
            "--body-file",
            str(body_file),
            "--dry-run",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["answer_id"] == 99
    assert "dry_run=true" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]


@responses.activate
def test_suggest():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/suggest",
        json=[{"layer": "city", "id": "1", "text": "Berlin"}],
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "forms",
            "filling",
            "suggest",
            SID,
            "--question",
            "c1",
            "--text",
            "Ber",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["text"] == "Berlin"
