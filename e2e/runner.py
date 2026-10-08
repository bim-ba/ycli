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
import time
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
    """What a command left: ``stdout`` as text, and as the bytes it was when those matter."""

    exit_code: int
    stdout: str
    stderr: str
    stdout_bytes: bytes = b""

    @property
    def printed(self) -> bytes:
        """The bytes of stdout: as they came, or the text's own when no bytes were kept."""
        return self.stdout_bytes or self.stdout.encode()


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
            timeout=self._timeout_seconds,
            check=False,
        )
        # A download prints bytes that are no text: nothing here may fail on them.
        return CommandResult(
            completed.returncode,
            completed.stdout.decode(errors="replace"),
            completed.stderr.decode(errors="replace"),
            completed.stdout,
        )


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


# What a run makes up itself: the only variables whose value a public log may show. Every
# other one was read from the service or given by the owner (a login, an id, a uid).
OWN_VARIABLES = frozenset({"RUN", "TAG", "QUEUE", "FILES"})
# A learned value this short (a version, a count) is not looked for in free text: it would
# be found everywhere.
_SHORTEST_HIDDEN = 4


def named(variables: dict[str, str]) -> dict[str, str]:
    """``variables`` as a public log may show them: a learned value by its name.

    ``named({"RUN": "e2e-1", "login": "ivan"}) -> {"RUN": "e2e-1", "login": "<login>"}``.
    """
    return {
        name: value if name in OWN_VARIABLES else f"<{name}>" for name, value in variables.items()
    }


def hidden(text: str, variables: dict[str, str]) -> str:
    """``text`` with every learned value replaced by its name, then scrubbed.

    For what came back from a command: an error that repeats a login it was given.
    ``hidden("no access for ivan.petrov", {"login": "ivan.petrov"}) -> "no access for <login>"``.
    """
    learned = [
        (value, name)
        for name, value in variables.items()
        if name not in OWN_VARIABLES and len(value) >= _SHORTEST_HIDDEN
    ]
    for value, name in sorted(learned, key=lambda pair: -len(pair[0])):
        text = text.replace(value, f"<{name}>")
    return scrub(text)


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
    retried: list[str] | None = None,
) -> list[str]:
    """Run every step in order, then the registered cleanups last-in-first-out.

    ``read`` is given the reads of each step right after it; without it they are not run.
    ``retried`` is given a line for each step that was run again (:class:`~e2e.models.Retry`).
    A step that needs a variable nobody set is not run; the steps skipped are returned, each
    with what it lacked (``"wiki/page-content/grant: needs GRANTEE"``).

    Cleanups run whatever happens; a cleanup failure never replaces the step failure that came
    first, and fails the scenario only when every step passed (the janitor is the backstop).
    """
    variables = dict(variables)
    # Each cleanup as it is run, and as a public log may show it.
    cleanups: dict[str, tuple[list[str], str]] = {}
    skipped: list[str] = []
    try:
        for step in scenario.steps:
            missing = [name for name in step.needs if name not in variables]
            if missing:
                skipped.append(f"{scenario.name}/{step.id}: needs {', '.join(missing)}")
                continue
            _run_step(scenario, step, driver, variables, retried)
            if step.cleanup is not None:
                cleanups[step.id] = (
                    render_command(step.cleanup, variables),
                    shlex.join(render_command(step.cleanup, named(variables))),
                )
            for target in step.disarms:
                cleanups.pop(target, None)
            if read is not None and step.reads:
                read(driver, [render_command(command, variables) for command in step.reads])
    except BaseException:
        _clean_up(cleanups, driver, variables)
        raise
    failures = _clean_up(cleanups, driver, variables)
    if failures:
        raise ScenarioError(f"[{scenario.name}] cleanup failed: " + "; ".join(failures))
    return skipped


def _run_step(
    scenario: Scenario,
    step: Step,
    driver: Driver,
    variables: dict[str, str],
    retried: list[str] | None = None,
) -> None:
    where = f"[{scenario.name}/{step.id}]"
    arguments = render_command(step.run, variables)
    completed = driver.run(arguments)
    retries = 0
    while (
        completed.exit_code != 0
        and step.retry is not None
        and retries < step.retry.times
        and step.retry.when in (completed.stderr or completed.stdout)
    ):
        time.sleep(step.retry.pause_seconds)
        retries += 1
        completed = driver.run(arguments)
    if retries and retried is not None and step.retry is not None:
        # Said whether it passed or not: a refusal that needed a second try is still a refusal.
        outcome = "passed" if completed.exit_code == 0 else "failed"
        count = "1 retry" if retries == 1 else f"{retries} retries"
        retried.append(f"{scenario.name}/{step.id}: {outcome} after {count} ({step.retry.when})")
    if completed.exit_code != 0:
        after = f" (after {retries} retries)" if retries else ""
        shown = shlex.join(render_command(step.run, named(variables)))
        raise ScenarioError(
            f"{where} `ycli {shown}` exited {completed.exit_code}{after}: "
            f"{hidden(completed.stderr or completed.stdout, variables)}"
        )
    document = _parse(where, step, completed)
    for expression, wanted in step.expect.items():
        query = render(expression, variables)
        expected = render(wanted, variables) if isinstance(wanted, str) else wanted
        actual = search(query, document)
        if actual != expected:
            shown = named(variables)
            wanted_shown = render(wanted, shown) if isinstance(wanted, str) else wanted
            raise ScenarioError(
                f"{where} expected `{render(expression, shown)}` == {wanted_shown!r}, "
                f"got {hidden(repr(actual), variables)} (output {_shape(document)})"
            )
    for name, expression in step.save.items():
        expression = render(expression, variables)
        value = search(expression, document)
        if value is None:
            raise ScenarioError(f"{where} save {name}: `{expression}` matched nothing")
        variables[name] = str(value)


def _parse(where: str, step: Step, completed: CommandResult) -> Any:
    stdout = completed.stdout
    if step.output == "bytes":
        # Enough to tell a file from nothing and one format from another, and no content.
        printed = completed.printed
        return {"size": len(printed), "head": printed[:16].hex()}
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


def _clean_up(
    cleanups: dict[str, tuple[list[str], str]], driver: Driver, variables: dict[str, str]
) -> list[str]:
    """Run each cleanup newest first; report failures on stderr and return them."""
    failures: list[str] = []
    for arguments, shown in reversed(list(cleanups.values())):
        try:
            completed = driver.run(arguments)
        except Exception as error:  # a timeout must not stop the remaining cleanups
            failures.append(f"`ycli {shown}`: {hidden(repr(error), variables)}")
            continue
        if completed.exit_code != 0:
            failures.append(
                f"`ycli {shown}` exited {completed.exit_code}: "
                f"{hidden(completed.stderr or completed.stdout, variables)}"
            )
    for failure in failures:
        print(f"cleanup failed (the janitor retries): {failure}", file=sys.stderr)
    return failures
