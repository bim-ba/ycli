"""The live runner's own contract, offline against a scripted driver (``e2e/runner.py``)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from e2e.models import Scenario
from e2e.runner import CommandResult, Driver, ScenarioError, items, run_scenario, scrub, search
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

    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        sent.append(argv)
        return subprocess.CompletedProcess(argv, 0, b"{}", b"")

    monkeypatch.setattr(runner.shutil, "which", lambda *_args, **_kwargs: "/venv/bin/ycli")
    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    runner.CliDriver().run(["wiki", "pages", "delete", "7"])
    assert sent == [["/venv/bin/ycli", "-o", "json", "--yes", "wiki", "pages", "delete", "7"]]


class _Flaky(Driver):
    """Fails the first ``failures`` runs with ``said``, then answers ``{}``."""

    def __init__(self, failures: int, said: str) -> None:
        self.failures, self.said, self.calls = failures, said, 0

    def run(self, arguments: Sequence[str]) -> CommandResult:
        self.calls += 1
        if self.calls <= self.failures:
            return CommandResult(1, "", self.said)
        return CommandResult(0, "{}", "")


TRY_AGAIN = "Error: 412 Precondition Failed for POST https://x/_start: try again"
RETRY = {"when": "412 Precondition Failed", "times": 2, "pause_seconds": 0}


def test_a_step_is_run_again_only_on_the_failure_it_names(capsys):
    step: dict[str, object] = {"id": "start", "run": "sprints start 7", "retry": RETRY}
    driver = _Flaky(1, TRY_AGAIN)
    retried: list[str] = []
    run_scenario(_scenario(step), driver, {}, retried=retried)
    assert driver.calls == 2
    assert retried == ["s/start: passed after 1 retry (412 Precondition Failed)"]
    # Another failure is not the one named: it fails at once, as any step does.
    other = _Flaky(1, "Error: 403 Forbidden")
    with pytest.raises(ScenarioError, match="403 Forbidden"):
        run_scenario(_scenario(step), other, {}, retried=retried)
    assert other.calls == 1


def test_a_step_that_keeps_failing_fails_after_its_retries():
    step: dict[str, object] = {"id": "start", "run": "sprints start 7", "retry": RETRY}
    driver = _Flaky(9, TRY_AGAIN)
    retried: list[str] = []
    with pytest.raises(ScenarioError, match=r"\[s/start\] .* exited 1 \(after 2 retries\)"):
        run_scenario(_scenario(step), driver, {}, retried=retried)
    assert driver.calls == 3
    assert retried == ["s/start: failed after 2 retries (412 Precondition Failed)"]


@pytest.mark.parametrize("times", [0, 6])
def test_a_retry_is_a_few_times_never_forever(times):
    with pytest.raises(ValueError, match="times"):
        _scenario({"id": "a", "run": "x", "retry": {"when": "412", "times": times}})


PNG = bytes.fromhex("89504e470d0a1a0a") + b"\x00\xff" * 40


def test_a_step_can_hold_the_bytes_a_command_printed():
    """A download is not text: the step sees how many bytes came and how they begin."""
    driver = ScriptedDriver({"thumb": CommandResult(0, "", "", PNG)})
    held = {"size": len(PNG), "starts_with(head, '89504e47')": True}
    run_scenario(
        _scenario({"id": "a", "run": "thumb", "output": "bytes", "expect": held}), driver, {}
    )
    wrong = _scenario({"id": "a", "run": "thumb", "output": "bytes", "expect": {"size": 0}})
    with pytest.raises(ScenarioError, match=r"expected `size` == 0, got 88"):
        run_scenario(wrong, driver, {})


def test_the_installed_command_may_print_bytes_that_are_not_text(monkeypatch):
    import subprocess

    from e2e import runner

    def fake_run(argv: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(argv, 0, PNG, b"")

    monkeypatch.setattr(runner.shutil, "which", lambda *_args, **_kwargs: "/venv/bin/ycli")
    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    completed = runner.CliDriver().run(["tracker", "attachments", "thumbnails-download", "A-1"])
    assert completed.stdout_bytes == PNG
    assert completed.exit_code == 0


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


class _Refusing(Driver):
    """Answers ``me`` with a login, refuses every other command and repeats what it was given."""

    def run(self, arguments: Sequence[str]) -> CommandResult:
        if arguments[0] == "me":
            return CommandResult(0, json.dumps({"login": "ivan.petrov", "version": 3}), "")
        return CommandResult(1, "", f"denied: {' '.join(arguments)}")


def test_a_failed_step_prints_the_name_of_what_the_run_learned_not_its_value():
    """A log of the CI job is public: a login read from the service does not go into it."""
    scenario = _scenario(
        {"id": "me", "run": "me get", "save": {"login": "login", "version": "version"}},
        {
            "id": "board",
            "run": "boards create --name '${RUN} board' --owner ${login} --version ${version}",
        },
    )
    with pytest.raises(ScenarioError) as failed:
        run_scenario(scenario, _Refusing(), {"RUN": "e2e-1-ab12", "GRANTEE": "someone.else"})
    said = str(failed.value)
    assert said.startswith(
        "[s/board] `ycli boards create --name 'e2e-1-ab12 board' --owner '<login>' "
        "--version '<version>'` exited 1: "
    )
    # What the service said back is masked too; the run's own name stays, to find its objects.
    assert "ivan.petrov" not in said and "e2e-1-ab12" in said
    assert "--owner <login>" in said.split("exited 1: ")[1]


def test_what_the_owner_gave_and_what_an_expectation_compares_are_masked_too():
    scenario = _scenario(
        {"id": "me", "run": "me get", "save": {"login": "login"},
         "expect": {"login": "${GRANTEE}"}},
    )  # fmt: skip
    with pytest.raises(ScenarioError) as failed:
        run_scenario(scenario, _Refusing(), {"GRANTEE": "someone.else"})
    assert str(failed.value).startswith("[s/me] expected `login` == '<GRANTEE>', got ")
    assert "someone.else" not in str(failed.value)


def test_a_failed_cleanup_prints_the_name_too(capsys):
    scenario = _scenario(
        {"id": "me", "run": "me get", "save": {"login": "login"}, "cleanup": "users drop ${login}"}
    )
    with pytest.raises(
        ScenarioError, match=r"cleanup failed: `ycli users drop '<login>'` exited 1"
    ):
        run_scenario(scenario, _Refusing(), {})
    assert "ivan.petrov" not in capsys.readouterr().err


def test_a_listing_is_read_as_its_items_and_any_other_document_as_it_is():
    listing = {"items": [{"id": 1}], "truncated": True, "next": "t", "total": None}
    assert items(listing) == [{"id": 1}]
    # An object that only has a field called `items` is no listing.
    assert items({"items": [1], "name": "form"}) == {"items": [1], "name": "form"}
    assert items([1, 2]) == [1, 2]


def test_a_step_reads_a_listing_as_its_items_or_as_it_is_printed():
    printed = {"items": [{"id": 1}], "truncated": True, "next": "t", "total": None}
    driver = ScriptedDriver({"boards": _ok(printed)})
    run_scenario(_scenario({"id": "a", "run": "boards", "expect": {"length(@)": 1}}), driver, {})
    held = {"length(items)": 1, "truncated": True, "type(next)": "string"}
    whole: dict[str, object] = {"id": "a", "run": "boards", "output": "listing", "expect": held}
    run_scenario(_scenario(whole), driver, {})
