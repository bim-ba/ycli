"""Run a :class:`Scenario` through a :class:`Driver`; the live driver calls the real ``ycli``.

Logs of the CI job are public, so a failure names the step, the command and the expectation,
and shows at most a short scrubbed excerpt of what came back, never a full body or the
environment.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Any

import jmespath
import jmespath.functions

from e2e.settings import CREDENTIAL_VARIABLES

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from e2e.models import Scenario, Step

EXCERPT_CHARACTERS = 300
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
_LONG_NUMBER = re.compile(r"\b\d{13,}\b")  # Yandex account uids; page/issue ids are shorter
# A link that carries its own permission in the query (object storage signs downloads so):
# whoever holds it needs no token.
_SIGNED_LINK = re.compile(
    r"https?://[^\s'\"<>]*[?&](?:X-Amz-[A-Za-z-]+|sign(?:ature)?|sig)=[^\s'\"<>]*", re.IGNORECASE
)


class ScenarioError(AssertionError):
    """A step did not reach its expected state; the message is safe for a public log."""


@dataclass(frozen=True, slots=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str


class Driver(ABC):
    """Runs one ycli command, given its arguments after ``ycli -o json --yes``.

    ``--yes`` because a scenario or the janitor deletes on purpose and no one is there to confirm.
    """

    @abstractmethod
    def run(self, arguments: Sequence[str]) -> CommandResult: ...


class CliDriver(Driver):
    """The ``ycli`` installed next to this interpreter, never another one found on ``PATH``."""

    def __init__(self, timeout_seconds: float = 120) -> None:
        executable = shutil.which("ycli", path=str(Path(sys.executable).parent))
        if executable is None:
            raise RuntimeError(f"no ycli next to {sys.executable}; run through `uv run`")
        self._executable = executable
        self._timeout_seconds = timeout_seconds

    def run(self, arguments: Sequence[str]) -> CommandResult:
        completed = subprocess.run(
            [self._executable, "-o", "json", "--yes", *arguments],
            capture_output=True,
            text=True,
            timeout=self._timeout_seconds,
            check=False,
        )
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)


class _Functions(jmespath.functions.Functions):
    """JMESPath plus ``unique``, which the language lacks (pagination must not repeat keys)."""

    @jmespath.functions.signature({"types": ["array"]})
    def _func_unique(self, values: list[Any]) -> list[Any]:
        """``unique(['a', 'b', 'a']) -> ['a', 'b']``: first occurrences, order kept."""
        return list(dict.fromkeys(values))


_SEARCH_OPTIONS = jmespath.Options(custom_functions=_Functions())


def search(expression: str, document: Any) -> Any:
    """``search("length(unique([].key))", [{"key": "A"}, {"key": "A"}]) -> 1``."""
    return jmespath.search(expression, document, options=_SEARCH_OPTIONS)


def scrub(text: str) -> str:
    """A public-log-safe excerpt: credentials, signed links, emails and uids masked, then cut.

    ``scrub("by ivan@ya.ru")`` -> ``"by <email>"``.
    """
    for name in CREDENTIAL_VARIABLES:
        secret = os.environ.get(name)
        if secret:
            text = text.replace(secret, "<redacted>")
    text = _SIGNED_LINK.sub("<signed link>", text)
    text = _LONG_NUMBER.sub("<uid>", _EMAIL.sub("<email>", text))
    if len(text) > EXCERPT_CHARACTERS:
        return f"{text[:EXCERPT_CHARACTERS]}… ({len(text)} characters)"
    return text


def render(template: str, variables: dict[str, str]) -> str:
    """``render("${RUN} x", {"RUN": "e2e-1"}) -> "e2e-1 x"``; an unknown name fails loudly."""
    try:
        return Template(template).substitute(variables)
    except KeyError as error:
        raise ScenarioError(f"unknown variable ${{{error.args[0]}}} in {template!r}") from None


def render_command(template: str, variables: dict[str, str]) -> list[str]:
    """Split first, then substitute, so a value with spaces or quotes stays one argument."""
    return [render(token, variables) for token in shlex.split(template)]


def run_json(driver: Driver, arguments: Sequence[str]) -> Any:
    """Run a command that prints JSON and parse it; a non-zero exit raises with an excerpt."""
    completed = driver.run(arguments)
    if completed.exit_code != 0:
        raise ScenarioError(
            f"`ycli {shlex.join(arguments)}` exited {completed.exit_code}: "
            f"{scrub(completed.stderr or completed.stdout)}"
        )
    return json.loads(completed.stdout) if completed.stdout.strip() else None


def run_scenario(
    scenario: Scenario,
    driver: Driver,
    variables: dict[str, str],
    read: Callable[[Driver, Sequence[Sequence[str]]], None] | None = None,
) -> list[str]:
    """Run every step in order, then the registered cleanups last-in-first-out.

    ``read`` is given the reads of each step right after it; without it they are not run.
    A step that needs a variable nobody set is not run; the steps skipped are returned, each
    with what it lacked (``"wiki/page-content/grant: needs GRANTEE"``).

    Cleanups run whatever happens; a cleanup failure never replaces the step failure that came
    first, and fails the scenario only when every step passed (the janitor is the backstop).
    """
    variables = dict(variables)
    cleanups: dict[str, list[str]] = {}
    skipped: list[str] = []
    try:
        for step in scenario.steps:
            missing = [name for name in step.needs if name not in variables]
            if missing:
                skipped.append(f"{scenario.name}/{step.id}: needs {', '.join(missing)}")
                continue
            _run_step(scenario, step, driver, variables)
            if step.cleanup is not None:
                cleanups[step.id] = render_command(step.cleanup, variables)
            for target in step.disarms:
                cleanups.pop(target, None)
            if read is not None and step.reads:
                read(driver, [render_command(command, variables) for command in step.reads])
    except BaseException:
        _clean_up(cleanups, driver)
        raise
    failures = _clean_up(cleanups, driver)
    if failures:
        raise ScenarioError(f"[{scenario.name}] cleanup failed: " + "; ".join(failures))
    return skipped


def _run_step(scenario: Scenario, step: Step, driver: Driver, variables: dict[str, str]) -> None:
    where = f"[{scenario.name}/{step.id}]"
    arguments = render_command(step.run, variables)
    completed = driver.run(arguments)
    if completed.exit_code != 0:
        raise ScenarioError(
            f"{where} `ycli {shlex.join(arguments)}` exited {completed.exit_code}: "
            f"{scrub(completed.stderr or completed.stdout)}"
        )
    document = _parse(where, step, completed.stdout)
    for expression, wanted in step.expect.items():
        query = render(expression, variables)
        expected = render(wanted, variables) if isinstance(wanted, str) else wanted
        actual = search(query, document)
        if actual != expected:
            raise ScenarioError(
                f"{where} expected `{query}` == {expected!r}, got {scrub(repr(actual))}"
                f" (output {_shape(document)})"
            )
    for name, expression in step.save.items():
        expression = render(expression, variables)
        value = search(expression, document)
        if value is None:
            raise ScenarioError(f"{where} save {name}: `{expression}` matched nothing")
        variables[name] = str(value)


def _parse(where: str, step: Step, stdout: str) -> Any:
    if step.output == "text":
        return stdout
    if not stdout.strip():
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        raise ScenarioError(f"{where} output is not JSON: {scrub(stdout)}") from None


def _shape(document: Any) -> str:
    """The structure of an output without its values: ``{'key', 'status'}`` or ``list[131]``."""
    if isinstance(document, dict):
        return "keys " + ", ".join(sorted(document))
    if isinstance(document, list):
        return f"list[{len(document)}]"
    return type(document).__name__


def _clean_up(cleanups: dict[str, list[str]], driver: Driver) -> list[str]:
    """Run each cleanup newest first; report failures on stderr and return them."""
    failures: list[str] = []
    for arguments in reversed(list(cleanups.values())):
        try:
            completed = driver.run(arguments)
        except Exception as error:  # a timeout must not stop the remaining cleanups
            failures.append(f"`ycli {shlex.join(arguments)}`: {scrub(repr(error))}")
            continue
        if completed.exit_code != 0:
            failures.append(
                f"`ycli {shlex.join(arguments)}` exited {completed.exit_code}: "
                f"{scrub(completed.stderr or completed.stdout)}"
            )
    for failure in failures:
        print(f"cleanup failed (the janitor retries): {failure}", file=sys.stderr)
    return failures
