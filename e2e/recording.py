"""Record the real replies of the API as fixtures: ``pytest e2e --record`` (#143).

Nothing here is part of the product. A recording run drives the same scenarios through the
CLI in this process (:class:`InProcessDriver`) instead of the installed binary, so it can see
what the binary hides:

- every public method of every resource client is wrapped to say which operation is running
  (``tracker.issues.get``), the name a contract case uses;
- the core's network seam (``core.session.default_transport``) is replaced by
  :class:`RecordingTransport`, which lets a request through to the real API and hands the
  reply to the :class:`Recorder`;
- the recorder keeps the fullest good reply of each operation, scrubbed (:mod:`e2e.scrub`), as
  ``<service>/<resource>/<method>.json``. A fixture is never edited by hand: record again.

While the reads of a scenario run (its ``reads:`` list), the transport refuses any request
whose endpoint does not declare the effect ``read``, before it reaches the network.
"""

from __future__ import annotations

import contextlib
import contextvars
import functools
import importlib
import json
import pkgutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx2
from pydantic import BaseModel, SecretStr, ValidationError
from typer.testing import CliRunner

import ycli.yandex
from e2e.runner import CommandResult, Driver
from e2e.runner import scrub as scrub_excerpt
from e2e.scrub import dumped, scrub
from ycli.yandex.core.auth import IAMTokenAuth
from ycli.yandex.core.endpoint import ENDPOINT_EXTENSION, Effect
from ycli.yandex.core.resource import Resource
from ycli.yandex.registry import SERVICES

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

    import pytest

    from ycli.yandex.core.endpoint import Endpoint
    from ycli.yandex.service import Service

# Where the committed fixtures live: ``tests/fixtures/replies/<service>/<resource>/<method>.json``.
REPLIES = Path(__file__).parents[1] / "tests" / "fixtures" / "replies"
# The operation whose method is running, ``None`` outside one (a sign-in probe).
_OPERATION: contextvars.ContextVar[str | None] = contextvars.ContextVar("operation", default=None)


class NotAReadError(RuntimeError):
    """A request that would change the server was about to go out while only reads may."""


def resources(service: Service) -> dict[str, Resource]:
    """``resource name -> its client`` for ``service``, from a client that is never used."""
    client_class = service.client_class()
    if service.profile.oauth_token:
        client = client_class(oauth_token="-", organization_id="-", cloud_organization_id="-")
    else:
        auth = IAMTokenAuth(SecretStr("-"))
        client = client_class(auth=auth, organization_id="-", cloud_organization_id="-")
    with client:
        return {name: value for name, value in vars(client).items() if isinstance(value, Resource)}


def operations() -> dict[str, tuple[type, str]]:
    """``tracker.issues.get -> (IssuesClient, "get")`` for every operation of every service."""
    found: dict[str, tuple[type, str]] = {}
    owners: dict[type, str] = {}
    for service in SERVICES:
        for name, resource in resources(service).items():
            slug = f"{service.name}.{name}"
            if owners.setdefault(type(resource), slug) != slug:
                # One class under two names: a reply could not be told apart by its method.
                raise RuntimeError(
                    f"{type(resource).__name__} serves {owners[type(resource)]} and {slug}"
                )
            for method, value in vars(type(resource)).items():
                if callable(value) and not method.startswith("_"):
                    found[f"{slug}.{method}"] = (type(resource), method)
    return found


def public_names() -> frozenset[str]:
    """Every key that is public already: a field of a model of ycli, or one a service publishes.

    The published ones are the ``response`` names of ``scripts/api_snapshot/<service>.json``.
    """
    # A model is known only once its module is loaded, and the CLI loads a service on demand.
    for module in pkgutil.walk_packages(ycli.yandex.__path__, "ycli.yandex."):
        if "models" in module.name.split("."):
            importlib.import_module(module.name)
    names: set[str] = set()
    pending: list[type[BaseModel]] = [BaseModel]
    while pending:
        model = pending.pop()
        pending += model.__subclasses__()
        for name, info in model.model_fields.items():
            names.update(alias for alias in (name, info.alias) if isinstance(alias, str))
    for snapshot in (REPLIES.parents[2] / "scripts" / "api_snapshot").glob("*.json"):
        if snapshot.stem in {service.name for service in SERVICES}:
            for published in json.loads(snapshot.read_text(encoding="utf-8")):
                names.update(published.get("response", ()))
    return frozenset(names)


def _named(operation: str, method: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(method)
    def call(*args: Any, **kwargs: Any) -> Any:
        token = _OPERATION.set(operation)
        try:
            return method(*args, **kwargs)
        finally:
            _OPERATION.reset(token)

    return call


def reply_type(endpoint: Endpoint[Any]) -> Any:
    """What the reply of ``endpoint`` is read as: its ``response_type``, or what its parser returns.

    ``Any`` when neither says: a reply nothing reads, or raw bytes.
    """
    if endpoint.parser is not None:
        # Only the return annotation: the parameter's type is imported for type checkers alone.
        returned = endpoint.parser.__annotations__.get("return", Any)
        if not isinstance(returned, str):
            return returned
        # The annotation as written in the parser's own module, a name of that module.
        return eval(returned, getattr(endpoint.parser, "__globals__", {}))
    return Any if endpoint.response_type in (None, bytes) else endpoint.response_type


def _keys(value: Any) -> int:
    """How many keys ``value`` holds at every depth: ``{"a": {"b": 1}, "c": [{"d": 2}]}`` -> 4."""
    if isinstance(value, dict):
        return len(value) + sum(map(_keys, value.values()))
    return sum(map(_keys, value)) if isinstance(value, list) else 0


@dataclass
class Recorder:
    """Keeps the first good reply of each operation under ``directory``, and what it saw."""

    directory: Path
    public: frozenset[str] = field(default_factory=public_names)
    reads_only: bool = False
    recorded: dict[str, Path] = field(default_factory=dict)
    # How many keys the kept reply of each operation has: a fuller one replaces it.
    _keys_kept: dict[str, int] = field(default_factory=dict)
    unknown_keys: dict[str, list[str]] = field(default_factory=dict)
    # Requests sent outside any operation (the probes of ``auth status``): seen, never kept.
    unnamed: int = 0
    failed_reads: list[str] = field(default_factory=list)

    def note(self, endpoint: Endpoint[Any] | None, response: httpx2.Response) -> None:
        """Keep ``response`` when it is the fullest good reply so far of the running operation.

        The fullest, not the first: an issue read again once it is closed carries its
        resolution, and a fixture should show every key the scenarios make the API send.
        """
        operation = _OPERATION.get()
        if operation is None or endpoint is None:
            self.unnamed += 1
            return
        if not response.is_success:
            return
        fixture: dict[str, Any] = {"status": response.status_code}
        keys = 0
        if "json" in response.headers.get("content-type", "") and response.content:
            reply = scrub(response.json(), reply_type(endpoint), self.public)
            keys = _keys(reply.body)
            if operation in self.recorded and keys <= self._keys_kept[operation]:
                return
            fixture["body"] = reply.body
            # How many keys the model does not know: the number may only go down (the check
            # in tests/contract/test_recorded_replies.py), the names stay with whoever records.
            fixture["unknown_keys"] = len(set(reply.unknown_keys))
            self.unknown_keys.pop(operation, None)
            if reply.unknown_keys:
                self.unknown_keys[operation] = sorted(set(reply.unknown_keys))
            if reply_type(endpoint) is not Any:
                # A scrubbed reply must still be one its own model reads.
                try:
                    endpoint.parse(
                        httpx2.Response(
                            response.status_code, json=reply.body, request=response.request
                        )
                    )
                except Exception as error:
                    raise RuntimeError(
                        f"the scrubbed reply of {operation} no longer fits its model: "
                        f"{scrub_excerpt(str(error))}"
                    ) from None
        elif operation in self.recorded:
            return
        path = self.directory.joinpath(*operation.split(".")).with_suffix(".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dumped(fixture), encoding="utf-8")
        self.recorded[operation] = path
        self._keys_kept[operation] = keys

    def read(self, driver: Driver, commands: Sequence[Sequence[str]]) -> None:
        """Run the reads of a scenario; nothing that is not a read leaves this process."""
        self.reads_only = True
        try:
            for arguments in commands:
                # A second lock over the transport's: under --dry-run the product itself
                # holds a write and shows its plan. A read is sent as usual, a POST that
                # reads too: both locks go by the effect of the endpoint, not the method.
                completed = driver.run(["--dry-run", *arguments])
                if completed.exit_code != 0:
                    reason = scrub_excerpt(completed.stderr or completed.stdout)
                    self.failed_reads.append(f"{' '.join(arguments[:4])}: {reason}")
        finally:
            self.reads_only = False

    def summary(self) -> str:
        """What the run recorded, in numbers; safe for a public log."""
        unknown = sum(map(len, self.unknown_keys.values()))
        return "\n".join(
            [
                f"recorded {len(self.recorded)} of {len(operations())} operations "
                f"into {self.directory}",
                f"requests outside any operation, not kept: {self.unnamed}",
                f"reads that failed: {len(self.failed_reads)}",
                f"keys a model does not know: {unknown} in {len(self.unknown_keys)} operations",
            ]
        )

    def details(self) -> str:
        """The names behind :meth:`summary`: for a file outside the repository, never a log."""
        lines = [f"read failed: {failure}" for failure in self.failed_reads]
        for operation, keys in sorted(self.unknown_keys.items()):
            lines.append(f"{operation}: keys the model does not know: {', '.join(keys)}")
        return "\n".join(lines) + "\n"


class RecordingTransport(httpx2.BaseTransport):
    """The real network, with every reply shown to the recorder on its way back."""

    def __init__(self, recorder: Recorder, network: httpx2.Client) -> None:
        self._recorder = recorder
        self._network = network

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        endpoint = request.extensions.get(ENDPOINT_EXTENSION)
        if self._recorder.reads_only and (endpoint is None or endpoint.effect is not Effect.READ):
            raise NotAReadError(f"{request.method} {request.url.path} is not a read")
        response = self._network.send(request)
        self._recorder.note(endpoint, response)
        return response


class InProcessDriver(Driver):
    """The same CLI as the binary, run in this process so the recorder can see its requests.

    A failure is turned into the exit code and the message ``ycli.cli.app.main`` gives it.
    ``pause_seconds`` stands in for the start of a process: a search right after a write finds
    it only a moment later, and the scenarios were written against the binary's pace.
    """

    def __init__(self, pause_seconds: float = 1.0) -> None:
        self._pause_seconds = pause_seconds

    def run(self, arguments: Sequence[str]) -> CommandResult:
        from ycli.cli.app import app
        from ycli.cli.errors import exit_code_for, format_cli_error
        from ycli.settings import ProfileError
        from ycli.yandex.errors import YandexError

        time.sleep(self._pause_seconds)
        result = CliRunner().invoke(app, ["-o", "json", "--yes", *arguments])
        error = result.exception
        if isinstance(error, NotAReadError):
            raise error
        if isinstance(error, YandexError | ValidationError | ProfileError):
            return CommandResult(int(exit_code_for(error)), result.stdout, format_cli_error(error))
        if error is not None and not isinstance(error, SystemExit):
            raise error
        return CommandResult(result.exit_code, result.stdout, result.stderr)


@contextlib.contextmanager
def recording(
    monkeypatch: pytest.MonkeyPatch, directory: Path, network: httpx2.BaseTransport | None = None
) -> Iterator[Recorder]:
    """Wrap the operations and replace the network seam for as long as the block is open.

    ``network`` stands in for the real API (a test's ``httpx2.MockTransport``).
    """
    recorder = Recorder(directory)
    for operation, (owner, method) in operations().items():
        monkeypatch.setattr(owner, method, _named(operation, getattr(owner, method)))
    # One client for the run, not a bare transport per command: it reads the proxy settings of
    # the environment, and a command in this process never exits to close its connections.
    with httpx2.Client(transport=network) as client:
        monkeypatch.setattr(
            "ycli.yandex.core.session.default_transport",
            lambda: RecordingTransport(recorder, client),
        )
        yield recorder


def load(path: Path) -> dict[str, Any]:
    """One fixture file: ``{"status": 200, "body": …, "unknown_keys": 3}``.

    ``body`` and ``unknown_keys`` are absent for a reply that is not JSON.
    """
    return json.loads(path.read_text(encoding="utf-8"))
