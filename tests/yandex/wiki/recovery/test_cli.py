"""TDD for `wiki recovery` CLI (wiring-dependent: needs the recovery sub-app mounted)."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.wiki.yandex.net/v1"
runner = CliRunner()


@responses.activate
def test_recovery_restore_dumps_model_json():
    responses.add(
        responses.POST,
        f"{BASE}/recovery_tokens/tok-uuid/recover",
        json={"id": 42, "slug": "data/x"},
        status=200,
    )
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "recovery", "restore", "tok-uuid"])
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["id"] == 42 and out["slug"] == "data/x"
    assert responses.calls[0].request.method == "POST"
