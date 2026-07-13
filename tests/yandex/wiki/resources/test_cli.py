"""TDD for `wiki resources` CLI.

NOTE: these invoke the ROOT app, so they pass only AFTER the orchestrator mounts the
`resources` sub-app in ``wiki/cli.py`` (producer agents do not wire).
"""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.wiki.yandex.net/v1"
runner = CliRunner()


@responses.activate
def test_resources_list_dumps_flat_list():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/resources",
        json={"results": [{"type": "attachment", "item": {"name": "d.png"}}], "next_cursor": None},
        status=200,
    )
    result = runner.invoke(
        cli.app, ["--format", "json", "wiki", "resources", "list", "42", "--types", "attachment"]
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out[0]["type"] == "attachment"
    assert responses.calls[-1].request.params["types"] == "attachment"  # ty: ignore[unresolved-attribute]
