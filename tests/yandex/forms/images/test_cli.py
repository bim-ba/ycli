"""TDD for `forms images` CLI — upload (needs the resource mounted)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import FORMS_BASE as BASE

SID = "6818ceffe010db4f59d11329"
runner = CliRunner()


@responses.activate
def test_upload(tmp_path):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/images",
        json={"id": 7, "links": {}, "name": "logo.png", "check_status": "check"},
        status=201,
    )
    local = tmp_path / "logo.png"
    local.write_bytes(b"\x89PNGdata")
    res = runner.invoke(cli.app, ["--format", "json", "forms", "images", "upload", SID, str(local)])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["id"] == 7
