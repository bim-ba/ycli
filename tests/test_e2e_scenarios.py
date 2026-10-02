"""Offline guard for the live scenarios in ``e2e/``: every file parses, every command exists.

The live suite runs nightly, so a renamed command or option would otherwise surface a day
later; here it fails on the pull request. Each command is replayed through the real CLI with
``--help`` appended: Click resolves the command path and rejects unknown options before it
prints help, while required options and argument types are not checked.
"""

from __future__ import annotations

import re
import shlex
from typing import TYPE_CHECKING

import pytest
from e2e.catalog import load, scenario_paths
from pydantic import ValidationError
from typer.testing import CliRunner

from ycli.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


_VARIABLE = re.compile(r"\$\{\w+\}")


def _help_exit_code(command: str) -> int:
    """Exit code of ``ycli -o json <command> --help`` with every ``${var}`` set to ``0``."""
    arguments = [_VARIABLE.sub("0", token) for token in shlex.split(command)]
    return CliRunner().invoke(app, ["-o", "json", *arguments, "--help"]).exit_code


def _commands() -> list[object]:
    return [
        pytest.param(command, id=f"{load(path).name}:{command.split('$')[0].strip()}")
        for path in scenario_paths()
        for command in load(path).commands()
    ]


def test_every_service_has_a_scenario():
    services = {path.parent.name for path in scenario_paths()}
    assert services == {"tracker", "wiki", "forms"}


@pytest.mark.parametrize("command", _commands())
def test_scenario_command_exists(command: str):
    assert _help_exit_code(command) == 0, f"`ycli {command}` is not a valid command line"


@pytest.mark.parametrize(
    "command",
    [
        "tracker issuez create --queue ${QUEUE}",  # a typo'd command
        "tracker issues create --queue ${QUEUE} --summmary x",  # a typo'd option
    ],
)
def test_command_guard_bites(command: str):
    assert _help_exit_code(command) != 0


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "broken.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_a_typoed_scenario_command_is_caught(tmp_path):
    path = _write(tmp_path, "name: t\nsteps:\n  - {id: a, run: tracker issuez get KEY-1}\n")
    (command,) = load(path).commands()
    assert _help_exit_code(command) == 2


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("name: t\nsteps:\n  - {id: a, run: x, expct: {}}\n", "Extra inputs are not permitted"),
        ("name: t\nsteps:\n  - {id: a, run: x}\n  - {id: a, run: y}\n", "duplicate step id"),
        ("name: t\nsteps:\n  - {id: a, run: x, disarms: [b]}\n", "no earlier cleanup"),
        ("name: t\nsteps: []\n", "at least 1 item"),
    ],
)
def test_a_malformed_scenario_fails_to_load(tmp_path, text: str, message: str):
    with pytest.raises(ValidationError, match=message):
        load(_write(tmp_path, text))
