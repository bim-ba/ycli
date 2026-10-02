"""`tracker filters` refuses a --filter that is not a JSON object before sending anything."""

import re

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli


@pytest.mark.parametrize(
    ("command", "raw", "message"),
    [
        (["create", "--name", "X"], "not-json", "--filter must be valid JSON"),
        (["create", "--name", "X"], "[1, 2]", "--filter must be a JSON object"),
        (["update", "12345"], "{broken", "--filter must be valid JSON"),
    ],
)
def test_a_bad_filter_fails_before_sending(api, command, raw, message):
    res = CliRunner().invoke(cli.app, ["tracker", "filters", *command, "--filter", raw])
    assert res.exit_code != 0
    # CI forces colour: drop the escape codes and the panel border before matching the words.
    plain = re.sub(r"[│╭╮╰╯─]", " ", re.sub(r"\x1b\[[0-9;]*m", "", res.output))
    assert message in " ".join(plain.split())
    assert api.calls == []
