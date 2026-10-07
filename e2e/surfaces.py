"""Read through the CLI, then the same read through MCP and the SDK: ``pytest e2e --surfaces``.

ARCH-1 gives every operation one name on the three surfaces, and nothing here keeps a table
of names or parses a command line. A step runs through the CLI in this process
(:class:`~e2e.recording.InProcessDriver`), and :func:`listening` hears which method of which
resource client the command called and with what arguments: the CLI itself turns flags into
arguments. :class:`ThreeSurfaces` then calls the tool of that name and the method itself with
those arguments, and compares the three replies.

Only a read is repeated: a command that called one operation whose every request declares the
effect ``read``. A write runs once, as before. While a repeat runs, the transport refuses any
request that is not a read before it reaches the network.

What a run found is a :class:`Report`; it holds names, paths and shapes, never a value.
"""

from __future__ import annotations

import asyncio
import contextlib
import functools
import inspect
import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import httpx2
from fastmcp import Client
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, SecretStr
from pydantic_core import to_jsonable_python

from e2e.recording import NotAReadError, operations, public_names
from e2e.runner import CommandResult, Driver, ScenarioError, scrub
from ycli.mcp.selection import Selection
from ycli.mcp.server import build_server
from ycli.settings import AppConfig, Credentials
from ycli.yandex.core.endpoint import ENDPOINT_EXTENSION, Effect
from ycli.yandex.errors import YandexError
from ycli.yandex.factory import build_client
from ycli.yandex.models import WIRE
from ycli.yandex.registry import SERVICES

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

    import pytest
    from fastmcp.tools import Tool

# How many differing paths of one reply are kept: the first ones name the defect.
MAX_PATHS = 20
Surface = Literal["mcp", "sdk"]
_NO_JSON = object()
_INDEX = re.compile(r"\[\d+\]")


@dataclass
class Call:
    """One call of an operation: ``tracker.issues.get`` with ``{"issue_id": "A-1"}``."""

    operation: str
    arguments: dict[str, Any]
    defaults: dict[str, Any]
    effects: list[Effect | None] = field(default_factory=list)

    def is_read(self) -> bool:
        """Whether it sent something and all of it only read."""
        return bool(self.effects) and all(effect is Effect.READ for effect in self.effects)


@dataclass
class Listener:
    """What the commands of this process called, and the lock that holds a repeat to reads."""

    calls: list[Call] = field(default_factory=list)
    running: Call | None = None
    reads_only: bool = False

    def heard(self, operation: str, method: Callable[..., Any]) -> Callable[..., Any]:
        """``method`` wrapped to note its call; a call made inside another is part of it."""
        signature = inspect.signature(method)

        @functools.wraps(method)
        def call(*args: Any, **kwargs: Any) -> Any:
            if self.running is not None or self.reads_only:
                return method(*args, **kwargs)
            given = dict(signature.bind(*args, **kwargs).arguments)
            given.pop("self")
            defaults = {
                name: parameter.default
                for name, parameter in signature.parameters.items()
                if parameter.default is not inspect.Parameter.empty
            }
            self.running = Call(operation, given, defaults)
            self.calls.append(self.running)
            try:
                return method(*args, **kwargs)
            finally:
                self.running = None

        return call


class _Watched(httpx2.BaseTransport):
    """The transport that was there, with the effect of every request noted on its way out."""

    def __init__(
        self, listener: Listener, inner: httpx2.BaseTransport | None, network: httpx2.Client
    ) -> None:
        self._listener = listener
        self._inner = inner
        self._network = network

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        endpoint = request.extensions.get(ENDPOINT_EXTENSION)
        effect = None if endpoint is None else endpoint.effect
        if self._listener.reads_only and effect is not Effect.READ:
            raise NotAReadError(f"{request.method} {request.url.path} is not a read")
        if self._listener.running is not None:
            self._listener.running.effects.append(effect)
        if self._inner is not None:
            return self._inner.handle_request(request)
        return self._network.send(request)


@contextlib.contextmanager
def listening(monkeypatch: pytest.MonkeyPatch) -> Iterator[Listener]:
    """Hear every operation and every request for as long as the block is open.

    It goes over whatever stands at the network seam already: a recording run's transport,
    or a test's ``httpx2.MockTransport``.
    """
    listener = Listener()
    for operation, (owner, method) in operations().items():
        monkeypatch.setattr(owner, method, listener.heard(operation, getattr(owner, method)))
    from ycli.yandex.core import session

    before = session.default_transport
    with httpx2.Client() as network:
        monkeypatch.setattr(
            "ycli.yandex.core.session.default_transport",
            lambda: _Watched(listener, before(), network),
        )
        yield listener


def differences(one: Any, other: Any, path: str = "$") -> list[str]:
    """Where two replies differ, as paths with shapes and no value.

    ``differences({"a": 1, "b": [1]}, {"a": 2, "b": [1, 2]})`` ->
    ``["$.a: int != int", "$.b: list[1] != list[2]"]``.
    """
    if isinstance(one, dict) and isinstance(other, dict):
        found: list[str] = []
        for key in sorted(one.keys() | other.keys()):
            if key not in one or key not in other:
                found.append(f"{path}.{key}: only in the {'second' if key in other else 'first'}")
            else:
                found += differences(one[key], other[key], f"{path}.{key}")
        return found
    if isinstance(one, list) and isinstance(other, list) and len(one) == len(other):
        return [
            difference
            for index, (left, right) in enumerate(zip(one, other, strict=True))
            for difference in differences(left, right, f"{path}[{index}]")
        ]
    return [] if one == other else [f"{path}: {_shape(one)} != {_shape(other)}"]


def _shape(value: Any) -> str:
    return f"list[{len(value)}]" if isinstance(value, list) else type(value).__name__


def _where(difference: str) -> str:
    """The path of a difference: ``"$.a: int != int" -> "$.a"``."""
    return difference.split(": ", 1)[0]


def _moved(path: str, changed: Sequence[str]) -> bool:
    """Whether ``path`` lies at, under or over a path that changed between two reads."""
    return any(
        path == other or path.startswith((f"{other}.", f"{other}[")) or other.startswith(path)
        for other in changed
    )


@dataclass(frozen=True)
class Finding:
    """One place where a surface answered a read differently from the CLI.

    ``kind`` is ``time`` when the CLI itself answered differently there a moment later (the
    object moved between the calls: noise of the runner), and ``data`` when the CLI answered
    the same before and after and the surface answered something else: a defect.
    """

    operation: str
    surface: Surface
    kind: Literal["data", "time"]
    what: str


@dataclass
class Report:
    """What a run on three surfaces found; every line is safe for a public log."""

    public: frozenset[str] = field(default_factory=public_names)
    compared: dict[Surface, set[str]] = field(default_factory=lambda: {"mcp": set(), "sdk": set()})
    findings: list[Finding] = field(default_factory=list)
    # Why a command was not repeated, or a surface not asked: reason -> what it was.
    left_out: dict[str, set[str]] = field(default_factory=dict)
    # Where the surfaces are not equal before any call is made (:func:`unequal`).
    unequal: dict[str, list[str]] = field(default_factory=dict)

    def leave_out(self, reason: str, what: str) -> None:
        """Note that ``what`` was not compared, and why."""
        self.left_out.setdefault(reason, set()).add(what)

    def path(self, path: str) -> str:
        """``path`` with ``<key>`` for a key no model names, and no index: one line per field.

        ``"$.fields.ivan[3].id: str != str" -> "$.fields.<key>.id: str != str"``.
        """
        head, *rest = path.split(": ", 1)
        head = _INDEX.sub("[]", head)
        parts = [
            part if part == "$" or part.split("[")[0] in self.public else "<key>"
            for part in head.split(".")
        ]
        return ": ".join([".".join(parts), *rest])

    def data(self) -> list[Finding]:
        """The findings that are defects."""
        return [finding for finding in self.findings if finding.kind == "data"]

    def text(self) -> str:
        """The whole report."""
        lines = [
            f"reads compared with the CLI: {len(self.compared['mcp'])} operations through MCP, "
            f"{len(self.compared['sdk'])} through the SDK",
        ]
        for kind, title in (
            ("data", "DATA: a surface answered differently (defects)"),
            ("time", "TIME: the object changed between the calls (noise of the runner)"),
        ):
            found = sorted(
                {
                    f"{finding.operation} [{finding.surface}] {finding.what}"
                    for finding in self.findings
                    if finding.kind == kind
                }
            )
            lines.append(f"{title}: {len(found)}")
            lines += [f"  {line}" for line in found]
        for reason, names in sorted(self.left_out.items()):
            lines.append(f"not compared, {reason}: {len(names)}")
            lines += [f"  {name}" for name in sorted(names)]
        for title, names in self.unequal.items():
            lines.append(f"{title}: {len(names)}")
            lines += [f"  {name}" for name in names]
        return "\n".join(lines) + "\n"


def _document(result: Any) -> Any:
    """What the CLI prints for ``result`` as JSON, or ``_NO_JSON`` when it prints no JSON."""
    if isinstance(result, BaseModel):
        return json.loads(result.model_dump_json(by_alias=True))
    return result if result is None or isinstance(result, str | int) else _NO_JSON


def _holds_a_secret(value: Any) -> bool:
    if isinstance(value, SecretStr):
        return True
    if isinstance(value, BaseModel):
        return any(_holds_a_secret(item) for item in dict(value).values())
    if isinstance(value, dict):
        return any(map(_holds_a_secret, value.values()))
    return isinstance(value, list | tuple) and any(map(_holds_a_secret, value))


def tool_name(operation: str) -> str:
    """``tool_name("tracker.comments.import_") -> "tracker_comments_import"``."""
    return operation.replace(".", "_").rstrip("_")


def unequal(tools: dict[str, Tool]) -> dict[str, list[str]]:
    """Where a method and its tool are not one operation, read from their signatures.

    Two lists by their titles: the operations with no tool, and the ones whose method takes
    an argument its tool does not (``"wiki.pages.get: fields"``).
    """
    no_tool, wider = [], []
    for operation, (owner, method) in sorted(operations().items()):
        tool = tools.get(tool_name(operation))
        if tool is None:
            no_tool.append(operation)
            continue
        taken = set(inspect.signature(getattr(owner, method)).parameters) - {"self"}
        extra = sorted(taken - set(tool.parameters.get("properties") or {}))
        if extra:
            wider.append(f"{operation}: {', '.join(extra)}")
    return {
        "operations with no tool": no_tool,
        "operations whose method takes what the tool does not": wider,
    }


class ThreeSurfaces(Driver):
    """Runs a command as ``driver`` does, then repeats a read through MCP and the SDK."""

    def __init__(self, driver: Driver, listener: Listener) -> None:
        self._driver = driver
        self._listener = listener
        self._runner = asyncio.Runner()
        self._server = build_server(Selection())
        self._services = {service.name: service for service in SERVICES}
        self._tools = {
            tool.name: tool
            for listed in self._runner.run(self._server.list_tools())
            # As the server holds it: the listing drops the output schemas.
            if (tool := self._runner.run(self._server.get_tool(listed.name))) is not None
        }
        self.report = Report(unequal=unequal(self._tools))

    def close(self) -> None:
        """Close the loop the tools ran in."""
        self._runner.close()

    def run(self, arguments: Sequence[str]) -> CommandResult:
        """The command's result; what the other surfaces answered goes to the report."""
        del self._listener.calls[:]
        completed = self._driver.run(arguments)
        calls = list(self._listener.calls)
        command = " ".join(arguments[:3])
        if completed.exit_code != 0:
            return completed
        if len(calls) != 1:
            reason = "the command called no operation" if not calls else "several operations"
            self.report.leave_out(reason, command)
        elif not calls[0].is_read():
            self.report.leave_out("a write runs once", calls[0].operation)
        else:
            self._listener.reads_only = True
            try:
                self._compare(calls[0], arguments, completed.stdout)
            finally:
                self._listener.reads_only = False
        return completed

    def _compare(self, call: Call, arguments: Sequence[str], stdout: str) -> None:
        try:
            first = json.loads(stdout) if stdout.strip() else None
        except json.JSONDecodeError:
            self.report.leave_out("the command prints no JSON", call.operation)
            return
        answers: dict[Surface, Any] = {"sdk": self._sdk(call), "mcp": self._mcp(call)}
        again: Any = _NO_JSON
        for surface, answer in answers.items():
            if answer is _NO_JSON:
                continue
            self.report.compared[surface].add(call.operation)
            if isinstance(answer, _Failed):
                found = [f"failed: {answer.why}"]
            else:
                found = differences(first, answer)[:MAX_PATHS]
            if found and again is _NO_JSON:
                # Once more through the CLI: what it answers differently now moved by itself.
                repeated = self._driver.run(arguments)
                again = json.loads(repeated.stdout) if repeated.stdout.strip() else None
            changed = [] if again is _NO_JSON else [_where(d) for d in differences(first, again)]
            for difference in found:
                kind = "time" if _moved(_where(difference), changed) else "data"
                self.report.findings.append(
                    Finding(call.operation, surface, kind, self.report.path(difference))
                )

    def _sdk(self, call: Call) -> Any:
        service, resource, method = call.operation.split(".")
        client_class = self._services[service].client_class()
        try:
            with build_client(client_class, Credentials(), AppConfig()) as client:
                result = getattr(getattr(client, resource), method)(**call.arguments)
        except YandexError as error:
            return _Failed(scrub(str(error)))
        document = _document(result)
        if document is _NO_JSON:
            self.report.leave_out("the method returns what has no JSON form", call.operation)
        return document

    def _mcp(self, call: Call) -> Any:
        name = tool_name(call.operation)
        tool = self._tools.get(name)
        if tool is None:  # listed with the operations that have no tool
            return _NO_JSON
        known = tool.parameters.get("properties") or {}
        given = {
            argument: value
            for argument, value in call.arguments.items()
            if argument in known or value != call.defaults.get(argument, _NO_JSON)
        }
        wider = sorted(given.keys() - known.keys())
        if wider:
            self.report.leave_out(
                "the method takes what the tool does not", f"{call.operation}: {', '.join(wider)}"
            )
            return _NO_JSON
        if _holds_a_secret(list(given.values())):
            self.report.leave_out("an argument holds a secret", call.operation)
            return _NO_JSON
        sent = to_jsonable_python(given, by_alias=True, context=WIRE)
        try:
            data = self._runner.run(self._call_tool(name, sent))
        except ToolError as error:
            return _Failed(scrub(str(error)))
        wrapped = tool.output_schema and tool.output_schema.get("x-fastmcp-wrap-result")
        return (data or {}).get("result") if wrapped else data

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        async with Client(self._server) as client:
            return (await client.call_tool(name, arguments)).structured_content


@dataclass(frozen=True)
class _Failed:
    """A surface that answered a read with an error where the CLI answered."""

    why: str


def fail_on_data(report: Report, seen: int) -> None:
    """Raise when a surface answered a read differently from the CLI (``--surfaces strict``).

    ``seen`` is how many such findings the report held before the scenario ran.
    """
    found = report.data()[seen:]
    if found:
        raise ScenarioError(
            f"{len(found)} differences between the surfaces: "
            + "; ".join(f"{f.operation} [{f.surface}] {f.what}" for f in found[:5])
        )
