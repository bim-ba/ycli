"""`tracker boards list` refuses a negative --limit."""

from typer.testing import CliRunner

import ycli.cli.app as cli


def test_a_negative_limit_fails_before_sending(api):
    res = CliRunner().invoke(cli.app, ["tracker", "boards", "list", "--limit", "-5"])
    assert res.exit_code == 2
    assert api.calls == []
