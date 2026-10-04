"""Forms CLI arguments refused before any request is sent."""

import re

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli

SID = "686d0a1b2c3d4e5f00000070"


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["files", "verify", SID], "at least one --path"),
        (["files", "verify", SID, "--path", "a", "--url", "u", "--url", "v"], "count must match"),
        (["files", "delete"], "--path and/or --url"),
        (
            ["questions", "create", SID, "--type", "matrix", "--label", "x"],
            "'matrix' is not one of",
        ),
        (["questions", "create", SID], "--type (with flags) or --body-file"),
        (["surveys", "create", "--name", "x", "--field", "no-equals"], "key=value"),
        (["keysets", "create", SID, "--name", "x", "--total", "1"], "--enabled"),
        (["conditions", "submit", "create", SID], "--operator and at least one --item"),
    ],
)
def test_bad_arguments_fail_before_sending(argv, message):
    res = CliRunner().invoke(cli.app, ["forms", *argv])
    assert res.exit_code != 0
    # CI forces colour: drop the escape codes and the panel border before matching the words.
    plain = re.sub(r"[│╭╮╰╯─]", " ", re.sub(r"\x1b\[[0-9;]*m", "", res.output))
    assert message in " ".join(plain.split())
