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
from e2e.conftest import of_service
from e2e.models import Scenario
from e2e.settings import CREDENTIAL_VARIABLES, OPTIONAL_VARIABLES, missing_credentials
from pydantic import ValidationError
from typer.testing import CliRunner

from ycli.cli.app import app
from ycli.settings import SERVICE_ACCOUNT_KEY_FILE_ENV
from ycli.yandex.registry import SERVICES

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
    assert services == {service.name for service in SERVICES}


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


def test_a_scenario_is_named_after_the_directory_of_its_service():
    """The nightly run is one job per service, picked by the first part of the name."""
    assert not [
        str(path) for path in scenario_paths() if not of_service(load(path).name, path.parent.name)
    ]
    assert of_service("wiki/page-lifecycle", None)
    assert not of_service("wiki/page-lifecycle", "forms")


def test_a_step_needs_only_a_variable_the_settings_know():
    """A typo in ``needs`` would skip the step for ever, and say only that it was skipped."""
    assert not [
        f"{load(path).name}/{step.id}: {name}"
        for path in scenario_paths()
        for step in load(path).steps
        for name in step.needs
        if name not in OPTIONAL_VARIABLES
    ]


def _only(monkeypatch, **environment: str) -> None:
    for variable in (*CREDENTIAL_VARIABLES, SERVICE_ACCOUNT_KEY_FILE_ENV):
        monkeypatch.delenv(variable, raising=False)
    for variable, value in environment.items():
        monkeypatch.setenv(variable, value)


def test_a_service_is_reached_with_what_its_own_profile_takes(monkeypatch):
    """One rule for every service: no service is named in the rule."""
    profiles = {service.name: service.profile for service in SERVICES}
    _only(monkeypatch, YANDEX_ID_OAUTH_TOKEN="t", YANDEX_ID_ORGANIZATION_ID="o")
    assert missing_credentials(profiles["tracker"]) is None
    # DataLens takes no OAuth token and no Yandex 360 organization.
    assert missing_credentials(profiles["datalens"]) == (
        "set YANDEX_CLOUD_IAM_TOKEN or YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_FILE or "
        "YANDEX_CLOUD_SERVICE_ACCOUNT_KEY and YANDEX_CLOUD_ORGANIZATION_ID"
    )
    _only(monkeypatch, YANDEX_CLOUD_IAM_TOKEN="t", YANDEX_CLOUD_ORGANIZATION_ID="c")
    assert missing_credentials(profiles["datalens"]) is None
    # Tracker takes either way to sign in and either kind of organization.
    assert missing_credentials(profiles["tracker"]) is None
    _only(monkeypatch, YANDEX_CLOUD_IAM_TOKEN="t")
    assert missing_credentials(profiles["wiki"]) == (
        "set YANDEX_ID_ORGANIZATION_ID or YANDEX_CLOUD_ORGANIZATION_ID"
    )


def test_a_scenario_that_leaves_a_permanent_trace_runs_only_on_purpose():
    """What the API cannot delete is made once, by hand: never by a nightly run."""
    from e2e.conftest import kept_out

    step = {"id": "a", "run": "tracker statuses create --key k --type new"}
    leaves = Scenario.model_validate({"name": "tracker/x", "permanent": True, "steps": [step]})
    plain = Scenario.model_validate({"name": "tracker/y", "steps": [step]})
    assert kept_out(leaves, permanent=False) == (
        "leaves objects the API cannot delete: run it on purpose with --permanent"
    )
    assert kept_out(leaves, permanent=True) is None
    assert kept_out(plain, permanent=False) is None


def test_no_scenario_that_runs_by_itself_is_marked_permanent_and_smoke():
    """A pull request's run must never be the one that leaves a trace."""
    for path in scenario_paths():
        scenario = load(path)
        assert not (scenario.permanent and scenario.smoke), scenario.name
