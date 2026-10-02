"""`tracker links add` accepts only the relationship verbs Tracker knows."""

from typer.testing import CliRunner

import ycli.cli.app as cli


def test_an_unknown_relationship_fails_before_sending(api):
    res = CliRunner().invoke(cli.app, ["tracker", "links", "add", "DE-1", "bogus", "DE-2"])
    assert res.exit_code == 2
    assert api.calls == []
