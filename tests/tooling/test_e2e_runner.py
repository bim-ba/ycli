"""The live runner's own contract, offline against a scripted driver (``e2e/runner.py``)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from e2e.models import Scenario
from e2e.runner import CommandResult, Driver, ScenarioError, run_scenario, scrub, search
from e2e.settings import OPTIONAL_VARIABLES, optional_variables

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


def test_scrub_masks_a_signed_link_whole():
    """Whoever holds such a link reads the file with no token; a log of the CI job is public."""
    link = (
        "https://storage.example.net/exports/a.xlsx?X-Amz-Credential=MADEUPKEYID%2Fs3"
        "&X-Amz-Expires=259200&X-Amz-Signature=0123456789abcdef"
    )
    assert scrub(f"got {{'href': '{link}'}} instead") == "got {'href': '<signed link>'} instead"
    assert scrub("see https://x.example/f?sign=abc123&ts=1") == "see <signed link>"
    # A link that signs nothing stays: a failure should still say which address it was.
    assert scrub("GET https://api.example.net/v1/pages?slug=a") == (
        "GET https://api.example.net/v1/pages?slug=a"
    )


def test_scrub_masks_emails_and_uids():
    assert scrub("by ivan.p@yandex.ru uid 1130000012345678 id 50427846") == (
        "by <email> uid <uid> id 50427846"
    )


def test_the_cli_driver_confirms_deletes(monkeypatch):
    """Scenarios and the janitor delete on purpose, and an unattended run has no one to ask."""
    import subprocess

    from e2e import runner

    sent: list[list[str]] = []

    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        sent.append(argv)
        return subprocess.CompletedProcess(argv, 0, "{}", "")

    monkeypatch.setattr(runner.shutil, "which", lambda *_args, **_kwargs: "/venv/bin/ycli")
    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    runner.CliDriver().run(["wiki", "pages", "delete", "7"])
    assert sent == [["/venv/bin/ycli", "-o", "json", "--yes", "wiki", "pages", "delete", "7"]]


def test_a_step_that_needs_a_variable_nobody_set_is_skipped_with_its_cleanup():
    scenario = _scenario(
        {"id": "make", "run": "wiki pages create", "save": {"id": "id"}},
        {"id": "grant", "run": "wiki access create ${id} ${GRANTEE}", "needs": ["GRANTEE"],
         "cleanup": "wiki access clear ${id}"},
        {"id": "delete", "run": "wiki pages delete ${id}"},
    )  # fmt: skip
    driver = ScriptedDriver({"wiki pages create": _ok({"id": 7})})
    assert run_scenario(scenario, driver, {}) == ["s/grant: needs GRANTEE"]
    assert driver.calls == [["wiki", "pages", "create"], ["wiki", "pages", "delete", "7"]]
    driver = ScriptedDriver({"wiki pages create": _ok({"id": 7})})
    assert run_scenario(scenario, driver, {"GRANTEE": "42"}) == []
    assert ["wiki", "access", "create", "7", "42"] in driver.calls
    assert driver.calls[-1] == ["wiki", "access", "clear", "7"]


def test_the_optional_variables_are_the_ones_the_environment_sets(monkeypatch):
    for variable in OPTIONAL_VARIABLES.values():
        monkeypatch.delenv(variable, raising=False)
    assert optional_variables() == {}
    monkeypatch.setenv("YCLI_E2E_QUEUE_2", "MOVE")
    monkeypatch.setenv("YCLI_E2E_GRANTEE", "")
    assert optional_variables() == {"QUEUE_2": "MOVE"}


FOUND = "[?login == '${LOGIN}'] | [0].uid"


def test_a_save_expression_may_use_a_variable():
    """Finding one item of a listing by a value the run was given."""
    scenario = _scenario(
        {"id": "find", "run": "tracker users list", "save": {"uid": FOUND}},
        {"id": "use", "run": "tracker users get ${uid}"},
    )
    driver = ScriptedDriver(
        {"tracker users list": _ok([{"login": "ann", "uid": 1}, {"login": "bob", "uid": 2}])}
    )
    run_scenario(scenario, driver, {"LOGIN": "bob"})
    assert driver.calls[-1] == ["tracker", "users", "get", "2"]
