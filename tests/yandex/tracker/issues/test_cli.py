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
    assert len(json.loads(res.stdout)) == 5
    assert "stopped at 5 items; more may be available" in res.stderr
