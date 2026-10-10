"""`tracker issues list --limit`: a capped listing says so on stderr, keeping stdout clean."""

import json

from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE


def test_a_capped_listing_warns_on_stderr(api):
    page = [{"key": f"DE-{number}"} for number in range(1, 101)]
    api.add("POST", f"{BASE}/issues/_search", json=page, headers={"X-Total-Pages": "3"})
    res = CliRunner().invoke(
        cli.app, ["-o", "json", "tracker", "issues", "list", "--queue", "DE", "--limit", "5"]
    )
    assert res.exit_code == 0, res.output
    assert len(json.loads(res.stdout)["items"]) == 5
    # One line says it, with the token to go on from; the log says nothing of it.
    assert "stopped at 5; go on with: ycli tracker issues list --next " in res.stderr
    assert "WARNING" not in res.stderr
