"""Renamed CLI commands keep working under their old names, hidden and deprecated (#104)."""

import inspect
from collections.abc import Callable, Mapping
from typing import Any

from typer.testing import CliRunner

from tests.cli_aliases import CLI_ALIASES
from tests.hosts import TRACKER_BASE
from tests.snapshots._surface import cli_hidden_leaves, cli_leaves
from ycli.cli.app import app


def _parameters(command: Any) -> dict[str, tuple[str, ...]]:
    return {parameter.name or "": tuple(parameter.opts) for parameter in command.params}


def alias_problems(
    hidden: Mapping[str, Any], visible: Mapping[str, Any], aliases: Mapping[str, str]
) -> list[str]:
    """What is wrong between the hidden commands, the visible ones and the alias table."""
    problems = [
        f"{path}: hidden but not in CLI_ALIASES" for path in sorted(set(hidden) - set(aliases))
    ]
    problems += [
        f"{old}: in CLI_ALIASES but not a hidden command"
        for old in sorted(set(aliases) - set(hidden))
    ]
    for old, new in sorted(aliases.items()):
        if old not in hidden:
            continue
        if new not in visible:
            problems.append(f"{old}: its target {new!r} is not a visible command")
            continue
        old_command, new_command = hidden[old], visible[new]
        if inspect.unwrap(old_command.callback) is not inspect.unwrap(new_command.callback):
            problems.append(f"{old}: not the callback of {new!r}")
        if _parameters(old_command) != _parameters(new_command):
            problems.append(f"{old}: parameters differ from {new!r}")
    return problems


def test_every_old_name_is_a_hidden_alias_of_a_visible_command():
    assert alias_problems(cli_hidden_leaves(), cli_leaves(), CLI_ALIASES) == []


def test_the_alias_check_bites():
    visible = {"tracker boards update": _FakeCommand(_callback_a, ["--name"])}
    hidden = {"tracker boards edit": _FakeCommand(_callback_a, ["--name"])}
    table = {"tracker boards edit": "tracker boards update"}
    assert alias_problems(hidden, visible, table) == []
    assert alias_problems(
        {**hidden, "tracker boards add": hidden["tracker boards edit"]}, visible, table
    ) == ["tracker boards add: hidden but not in CLI_ALIASES"]
    assert alias_problems({}, visible, table) == [
        "tracker boards edit: in CLI_ALIASES but not a hidden command"
    ]
    assert alias_problems(hidden, {}, table) == [
        "tracker boards edit: its target 'tracker boards update' is not a visible command"
    ]
    other = {"tracker boards edit": _FakeCommand(_callback_b, ["--name"])}
    assert alias_problems(other, visible, table) == [
        "tracker boards edit: not the callback of 'tracker boards update'"
    ]
    wrong = {"tracker boards edit": _FakeCommand(_callback_a, ["--title"])}
    assert alias_problems(wrong, visible, table) == [
        "tracker boards edit: parameters differ from 'tracker boards update'"
    ]


def _callback_a() -> None: ...


def _callback_b() -> None: ...


class _FakeCommand:
    def __init__(self, callback: Callable[[], None], options: list[str]) -> None:
        self.callback = callback
        self.params = [type("Parameter", (), {"name": "name", "opts": options})()]


def test_an_alias_gets_injection_and_the_global_options_and_warns(api):
    api.add("PATCH", f"{TRACKER_BASE}/boards/51", json={"id": 51, "name": "Renamed"})
    result = CliRunner().invoke(
        app, ["tracker", "boards", "edit", "51", "--name", "Renamed", "-o", "yaml"]
    )
    assert result.exit_code == 0, result.output
    assert "name: Renamed" in result.stdout  # the client was injected; -o is read after the leaf
    assert "deprecated" in result.stderr


def test_the_old_nested_dashboard_path_still_runs(api):
    api.add("POST", f"{TRACKER_BASE}/dashboards/11/widgets/cycleTime", json={"id": 7}, status=201)
    result = CliRunner().invoke(
        app,
        ["tracker", "dashboards", "add-widget", "cycletime", "11", "--description", "Cycle time"],
    )
    assert result.exit_code == 0, result.output
    assert "deprecated" in result.stderr
