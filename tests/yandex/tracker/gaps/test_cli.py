"""`tracker gaps create` refuses an incomplete or malformed absence before sending anything."""

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli

WINDOW = ["--from", "2026-07-01T00:00Z", "--to", "2026-07-02T00:00Z"]


@pytest.mark.parametrize(
    "argv",
    [
        [],  # nothing to create
        ["--user", "ann", *WINDOW],  # no --workflow
        ["--workflow", "trip", *WINDOW],  # no --user
        ["--user", "ann", "--workflow", "trip", "--from", "2026-07-01T00:00Z"],  # no --to
        ["--gap", "{oops"],  # malformed JSON
    ],
)
def test_an_incomplete_or_malformed_absence_is_a_usage_error(api, argv):
    result = CliRunner().invoke(cli.app, ["tracker", "gaps", "create", *argv])
    assert result.exit_code == 2
    assert api.calls == []
