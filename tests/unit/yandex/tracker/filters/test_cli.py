"""`tracker filters` refuses a --filter that is not JSON; any valid JSON is sent as given."""

import re

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE


@pytest.mark.parametrize(
    ("command", "raw", "message"),
    [
        (["create", "--name", "X"], "not-json", "--filter must be valid JSON"),
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


def test_a_filter_that_is_not_an_object_is_sent_as_given(api):
    api.add("POST", f"{BASE}/filters/", json={"id": 1, "name": "X"})
    res = CliRunner().invoke(
        cli.app, ["tracker", "filters", "create", "--name", "X", "--filter", "[1, 2]"]
    )
    assert res.exit_code == 0
    assert api.body() == {"name": "X", "filter": [1, 2]}
