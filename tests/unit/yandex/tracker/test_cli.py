"""Tracker options that go in pairs: one alone builds no value to send (#296)."""

import re

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE


def _plain(output: str) -> str:
    # CI forces colour: drop the escape codes and the panel border before matching the words.
    return " ".join(re.sub(r"[│╭╮╰╯─]", " ", re.sub(r"\x1b\[[0-9;]*m", "", output)).split())


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["fields", "update", "f1", "--option", "a"], "--option and --options-type go together"),
        (
            ["fields", "update", "f1", "--options-type", "FixedListOptionsProvider"],
            "--option and --options-type go together",
        ),
        (
            ["checklists", "create", "TEST-1", "--text", "step", "--deadline", "2027-01-01"],
            "--deadline and --deadline-type go together",
        ),
        (
            ["checklists", "create", "TEST-1", "--text", "step", "--deadline-type", "date"],
            "--deadline and --deadline-type go together",
        ),
    ],
)
def test_half_of_a_pair_is_a_usage_error_that_names_both_options(api, argv, message):
    result = CliRunner().invoke(cli.app, ["tracker", *argv])
    assert result.exit_code == 2
    assert message in _plain(result.output)
    assert api.calls == []


def test_neither_option_of_a_pair_sends_no_block(api):
    api.add("PATCH", f"{BASE}/fields/f1", json={"id": "f1"})
    result = CliRunner().invoke(cli.app, ["tracker", "fields", "update", "f1", "--name-en", "F"])
    assert result.exit_code == 0, result.output
    assert api.body() == {"name": {"en": "F"}}
