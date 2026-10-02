"""TDD for `forms operations` CLI (wiring-dependent — run by the integrator after mount)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import FORMS_BASE as BASE

OID = "op-4a1b"
runner = CliRunner()


@responses.activate
def test_get_dumps_operation_status():
    responses.add(
        responses.GET,
        f"{BASE}/operations/{OID}",
        json={"id": OID, "status": "wait", "message": "running"},
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "operations", "get", OID])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["id"] == OID and out["status"] == "wait"
