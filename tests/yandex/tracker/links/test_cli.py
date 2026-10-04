"""`tracker links add` sends the relationship as it is given; the known verbs are in the help."""

from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE


def test_a_relationship_outside_the_known_set_is_sent_as_given(api):
    api.add("POST", f"{BASE}/issues/DE-1/links", json={"id": 1})
    res = CliRunner().invoke(cli.app, ["tracker", "links", "add", "DE-1", "bogus", "DE-2"])
    assert res.exit_code == 0, res.output
    assert api.body() == {"relationship": "bogus", "issue": "DE-2"}
