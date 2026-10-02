"""`tracker workflows` options that fail before anything is sent."""

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli


@pytest.mark.parametrize(
    ("argv", "option"),
    [
        (["create", "--name", "X", "--initial-action", "{oops"], "--initial-action"),
        (["create", "--name", "X", "--initial-action", "{}", "--step", "nope"], "--step"),
        (["update", "W1", "--version", "1", "--step", "["], "--step"),
        (["update", "W1", "--version", "1", "--initial-action", "{"], "--initial-action"),
        (
            ["create", "--name", "X", "--initial-action", "{}", "--issue-type-resolution", "x"],
            "--issue-type-resolution",
        ),
        (["update-action", "W1", "open", "go", "--version", "1", "--action", "{"], "--action"),
    ],
)
def test_malformed_json_is_a_usage_error_before_any_request(api, argv, option):
    result = CliRunner().invoke(cli.app, ["tracker", "workflows", *argv])
    assert result.exit_code == 2
    assert api.calls == []
    assert "must be valid JSON" in result.output or option in result.output
