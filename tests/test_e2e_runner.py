"""The live runner's own contract, offline against a scripted driver (``e2e/runner.py``)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from e2e.models import Scenario
from e2e.runner import CommandResult, Driver, ScenarioError, run_scenario, scrub, search

if TYPE_CHECKING:
    from collections.abc import Sequence


@pytest.fixture(autouse=True)
def _no_credentials(monkeypatch):
    """The shared fake credentials ("t", "o") would be masked inside every word."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID")


class ScriptedDriver(Driver):
    """Answers each command from ``answers`` (by its first words) and records every call."""

    def __init__(self, answers: dict[str, CommandResult]) -> None:
        self.answers = answers
        self.calls: list[list[str]] = []

    def run(self, arguments: Sequence[str]) -> CommandResult:
        self.calls.append(list(arguments))
        for prefix, result in self.answers.items():
            if " ".join(arguments).startswith(prefix):
                return result
        return CommandResult(0, "", "")


def _ok(document: object) -> CommandResult:
    return CommandResult(0, json.dumps(document), "")


def _scenario(*steps: dict[str, object]) -> Scenario:
    return Scenario.model_validate({"name": "s", "steps": list(steps)})


def test_saved_values_and_variables_reach_later_commands():
    driver = ScriptedDriver({"make": _ok({"key": "Q-1"})})
    scenario = _scenario(
        {"id": "a", "run": 'make --name "${RUN} x"', "save": {"key": "key"}},
        {"id": "b", "run": "use ${key}"},
    )
    run_scenario(scenario, driver, {"RUN": "e2e-1"})
    assert driver.calls == [["make", "--name", "e2e-1 x"], ["use", "Q-1"]]


def test_cleanups_run_newest_first_and_a_disarmed_one_is_skipped():
    driver = ScriptedDriver({"make": _ok({"id": 7})})
    scenario = _scenario(
        {"id": "a", "run": "make", "save": {"id": "id"}, "cleanup": "drop a ${id}"},
        {"id": "b", "run": "make", "cleanup": "drop b"},
        {"id": "c", "run": "make", "cleanup": "drop c"},
        {"id": "d", "run": "drop c", "disarms": ["c"]},
    )
    run_scenario(scenario, driver, {})
    assert driver.calls[-2:] == [["drop", "b"], ["drop", "a", "7"]]


def test_a_failed_expectation_still_cleans_up_and_is_not_masked(capsys):
    driver = ScriptedDriver(
        {
            "make": _ok({"status": "open", "owner": "ivan@ya.ru"}),
            "drop": CommandResult(1, "", "gone"),
        }
    )
    scenario = _scenario(
        {"id": "a", "run": "make", "cleanup": "drop"},
        {"id": "b", "run": "make", "expect": {"status": "closed"}},
    )
    with pytest.raises(ScenarioError, match=r"\[s/b\] expected `status` == 'closed', got 'open'"):
        run_scenario(scenario, driver, {})
    assert driver.calls[-1] == ["drop"]
    assert "cleanup failed" in capsys.readouterr().err


def test_a_failure_message_shows_the_shape_not_the_body():
    driver = ScriptedDriver({"make": _ok({"status": "open", "owner": "ivan@ya.ru"})})
    scenario = _scenario({"id": "a", "run": "make", "expect": {"status": "closed"}})
    with pytest.raises(ScenarioError) as raised:
        run_scenario(scenario, driver, {})
    assert "keys owner, status" in str(raised.value)
    assert "ivan" not in str(raised.value)


def test_a_cleanup_failure_fails_an_otherwise_green_scenario():
    driver = ScriptedDriver({"drop": CommandResult(1, "", "boom")})
    scenario = _scenario({"id": "a", "run": "make", "cleanup": "drop"})
    with pytest.raises(ScenarioError, match="cleanup failed: `ycli drop` exited 1: boom"):
        run_scenario(scenario, driver, {})


def test_a_non_zero_exit_names_the_step_with_a_scrubbed_excerpt(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "secret-token")
    driver = ScriptedDriver({"make": CommandResult(1, "", "denied for secret-token " + "x" * 400)})
    scenario = _scenario({"id": "a", "run": "make"})
    with pytest.raises(ScenarioError) as raised:
        run_scenario(scenario, driver, {})
    message = str(raised.value)
    assert message.startswith("[s/a] `ycli make` exited 1: denied for <redacted> ")
    assert "secret-token" not in message
    assert message.endswith("… (422 characters)")


def test_text_output_and_unknown_variables():
    driver = ScriptedDriver({"page": CommandResult(0, "# body e2e-1\n", "")})
    text = _scenario(
        {"id": "a", "run": "page", "output": "text", "expect": {"contains(@, 'body ${RUN}')": True}}
    )
    run_scenario(text, driver, {"RUN": "e2e-1"})
    with pytest.raises(ScenarioError, match=r"unknown variable \$\{nope\}"):
        run_scenario(_scenario({"id": "a", "run": "page ${nope}"}), driver, {})


def test_non_json_output_and_an_empty_save_fail_loudly():
    driver = ScriptedDriver({"page": CommandResult(0, "# not json", ""), "make": _ok({})})
    with pytest.raises(ScenarioError, match="output is not JSON"):
        run_scenario(_scenario({"id": "a", "run": "page"}), driver, {})
    with pytest.raises(ScenarioError, match="save key: `key` matched nothing"):
        run_scenario(_scenario({"id": "a", "run": "make", "save": {"key": "key"}}), driver, {})


def test_unique_counts_repeated_keys():
    issues = [{"key": "Q-1"}, {"key": "Q-2"}, {"key": "Q-1"}]
    assert search("length(unique([].key)) == length(@)", issues) is False
    assert search("length(unique([].key))", issues) == 2


def test_scrub_masks_emails_and_uids():
    assert scrub("by ivan.p@yandex.ru uid 1130000012345678 id 50427846") == (
        "by <email> uid <uid> id 50427846"
    )
