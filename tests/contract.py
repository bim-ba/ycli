"""The contract table: one :class:`Case` per way of reaching an operation, driving all surfaces.

A case names an SDK operation with its arguments, the CLI argv and the MCP tool call that
should reach it, and the exchanges the operation has with the API: each request it must send
and the canned reply. ``tests/test_contract.py`` runs every case through the SDK, the CLI and
the MCP server, and checks that each surface sent exactly these requests and that the MCP
tool's hints agree with the strongest effect among them.

A resource's cases live next to its other tests, in ``tests/yandex/<domain>/<resource>/cases.py``
as a module-level ``CASES`` list. Give every case distinct values (ids, fully populated
bodies): a value shared by two parameters, or an option left at its default, lets a surface
that drops or swaps it pass.

Example:
    >>> case = Case(
    ...     "tracker.issues.get",
    ...     args=("DE-7",),
    ...     cli=["tracker", "issues", "get", "DE-7"],
    ...     mcp=("tracker_issues_get", {"key": "DE-7"}),
    ...     exchanges=[(Sent("GET", "issues/DE-7"), Reply(json={"key": "DE-7"}))],
    ... )
    >>> case.id, case.expected_effect
    ('tracker.issues.get:tracker issues get', 'read')
"""

from __future__ import annotations

import importlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ycli.yandex.core.endpoint import _EFFECT_BY_METHOD, EFFECT_EXTENSION
from ycli.yandex.mcp import DESTRUCTIVE, RO, WRITE, WRITE_IDEMPOTENT

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    import httpx2

    from ycli.yandex.core.endpoint import Effect, Method

TESTS = Path(__file__).parent

# The MCP hints each effect implies (ARCH-3), and the order of effects from mildest to strongest:
# a tool that reads and then deletes is as destructive as its delete.
EFFECT_HINTS: dict[str, dict[str, bool]] = {
    "read": RO,
    "idempotent_write": WRITE_IDEMPOTENT,
    "write": WRITE,
    "destructive": DESTRUCTIVE,
}
HINT_KEYS = ("readOnlyHint", "destructiveHint", "idempotentHint")

# A request without a JSON body; distinct from a body that is JSON ``null``.
NO_BODY: Any = type("NoBody", (), {"__repr__": lambda self: "NO_BODY"})()
# A case that does not state what a surface returns; distinct from a stated ``None``.
UNSTATED: Any = type("Unstated", (), {"__repr__": lambda self: "UNSTATED"})()


@dataclass(frozen=True)
class Sent:
    """A request an operation must send: method, path under the service's base URL, query, body.

    ``params`` lists every query parameter (repeated ones as a list); ``json`` is the parsed body,
    ``files`` the parts of a ``multipart/form-data`` one (field → ``(filename, bytes)``) and
    ``content`` a raw body sent verbatim. ``headers`` must each be present with these values.
    """

    method: Method
    path: str
    params: Mapping[str, str | list[str]] = field(default_factory=dict)
    json: Any = NO_BODY
    files: Mapping[str, tuple[str, bytes]] | None = None
    content: bytes | None = None
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Sibling:
    """An SDK argument that is another resource of the same domain client (``client.<resource>``).

    For an operation that drives a second resource, as ``wiki.attachments.upload`` drives the
    upload sessions it is handed.
    """

    resource: str


@dataclass(frozen=True)
class Reply:
    """The API's canned answer to one request."""

    json: Any = None
    status: int = 200
    headers: Mapping[str, str] = field(default_factory=dict)
    content: bytes | None = None


@dataclass(frozen=True)
class Case:
    """One operation reached through the SDK, the CLI and the MCP server.

    ``operation`` is ``<domain>.<resource>.<method>`` on the SDK client. ``cli`` is the argv after
    ``ycli`` and ``mcp`` the tool name and arguments; either is ``None`` only for an operation
    listed in ``ARCH1_SURFACE_ASYMMETRIES`` or reached on that surface by another case.
    ``effect`` defaults to the strongest one the requests' methods imply; state it for a ``POST``
    that only reads. ``output`` is what the SDK must return, as the CLI prints it; state it for a
    result the client makes up itself (an ``Ack``) or one a limit cuts short, since a parsed reply
    is otherwise checked against the reply. ``cli_output`` is what the CLI prints when the
    command shapes the result instead of printing it whole (the bytes of a page's content).
    ``env`` is set while the CLI and MCP run (a small ``YCLI__HTTP__MAX_ITEMS`` shows that
    ``--all`` lifts the cap).
    """

    operation: str
    args: Sequence[Any] = field(default=(), kw_only=True)
    kwargs: Mapping[str, Any] = field(default_factory=dict, kw_only=True)
    cli: Sequence[str] | None = field(kw_only=True)
    mcp: tuple[str, Mapping[str, Any]] | None = field(kw_only=True)
    exchanges: Sequence[tuple[Sent, Reply]] = field(kw_only=True)
    effect: Effect | None = field(default=None, kw_only=True)
    output: Any = field(default=UNSTATED, kw_only=True)
    cli_output: Any = field(default=UNSTATED, kw_only=True)
    env: Mapping[str, str] = field(default_factory=dict, kw_only=True)

    @property
    def expected_effect(self) -> Effect:
        """The stated ``effect``, or the strongest one the requests' methods imply."""
        return self.effect or strongest(
            _EFFECT_BY_METHOD[sent.method] for sent, _ in self.exchanges
        )

    @property
    def domain(self) -> str:
        return self.operation.split(".")[0]

    @property
    def id(self) -> str:
        """``operation:how`` — pytest numbers the cases that share one."""
        how = " ".join(self.cli[:3]) if self.cli else self.mcp[0] if self.mcp else "sdk"
        return f"{self.operation}:{how}"


def mismatches(
    expected: Sequence[Sent], sent: Sequence[httpx2.Request], base_url: str
) -> list[str]:
    """How the requests a surface ``sent`` differ from the ``expected`` ones (empty: none).

    Example:
        >>> import httpx2
        >>> sent = [httpx2.Request("GET", "https://x.test/v1/a?b=1")]
        >>> mismatches([Sent("GET", "a", {"b": "1"})], sent, "https://x.test/v1")
        []
        >>> mismatches([Sent("GET", "a")], sent, "https://x.test/v1")
        ["request 0: params {'b': '1'} != {}"]
    """
    problems = []
    if len(sent) != len(expected):
        problems.append(f"sent {len(sent)} requests, expected {len(expected)}")
    for index, (want, got) in enumerate(zip(expected, sent, strict=False)):
        url = f"{base_url.rstrip('/')}/{want.path}"
        actual_url = str(got.url.copy_with(query=None))
        params = {
            name: values[0] if len(values) == 1 else values
            for name in got.url.params
            if (values := got.url.params.get_list(name))
        }
        problems += [
            f"request {index}: header {name} {got.headers.get(name)!r} != {value!r}"
            for name, value in want.headers.items()
            if got.headers.get(name) != value
        ]
        checks = [
            ("method", want.method, got.method),
            ("url", url, actual_url),
            ("params", dict(want.params), params),
        ]
        if want.files is not None:
            problems += _multipart_mismatches(index, want.files, got)
        elif want.content is not None:
            checks.append(("body", want.content, got.content))
        else:
            body = json.loads(got.content) if got.content else NO_BODY
            checks.append(("body", want.json, body))
        problems += [
            f"request {index}: {label} {actual!r} != {wanted!r}"
            for label, wanted, actual in checks
            if wanted != actual
        ]
    return problems


def _multipart_mismatches(
    index: int, files: Mapping[str, tuple[str, bytes]], got: httpx2.Request
) -> list[str]:
    if not got.headers.get("Content-Type", "").startswith("multipart/form-data"):
        return [f"request {index}: not a multipart/form-data body"]
    return [
        f"request {index}: no part {name!r} with file {filename!r} and its bytes"
        for name, (filename, data) in files.items()
        if f'name="{name}"; filename="{filename}"'.encode() not in got.content
        or data not in got.content
    ]


def strongest(effects: Iterable[Effect]) -> Effect:
    """The strongest of ``effects``.

    Example:
        >>> strongest(["read", "destructive", "write"])
        'destructive'
    """
    return max(effects, key=list(EFFECT_HINTS).index)


def lost_values(output: Any, reply: Any, where: str = "") -> list[str]:
    """Values of the API ``reply`` the parsed ``output`` lost (empty: it kept them all).

    Only shapes both sides share are compared: a key the model drops, or a reference the model
    flattens (``{"key": "bug"}`` → ``"bug"``), is not a loss; ``None`` where the reply had a value
    is.

    Example:
        >>> lost_values({"id": 1, "name": None}, {"id": 1, "name": "A", "extra": 2})
        ["name: None != 'A'"]
    """
    if isinstance(reply, dict) and isinstance(output, dict):
        return [
            problem
            for key in reply.keys() & output.keys()
            for problem in lost_values(output[key], reply[key], f"{where}{key}.")
        ]
    if isinstance(reply, list) and isinstance(output, list):
        if len(output) != len(reply):
            return [f"{where.rstrip('.') or 'items'}: {len(output)} items != {len(reply)}"]
        return [
            problem
            for index, (item, sent) in enumerate(zip(output, reply, strict=True))
            for problem in lost_values(item, sent, f"{where}{index}.")
        ]
    if reply is not None and (output is None or type(output) is type(reply)) and output != reply:
        return [f"{where.rstrip('.')}: {output!r} != {reply!r}"]
    return []


def reply_items(reply: Any) -> list[Any] | None:
    """The items of a listing reply: the reply itself, or the one list in its envelope.

    Example:
        >>> reply_items({"result": [1, 2], "links": {}}), reply_items({"a": [1], "b": [2]})
        ([1, 2], None)
    """
    if isinstance(reply, list):
        return reply
    lists = (
        [value for value in reply.values() if isinstance(value, list)]
        if isinstance(reply, dict)
        else []
    )
    return lists[0] if len(lists) == 1 else None


def output_problems(case: Case, output: Any) -> list[str]:
    """How the SDK's ``output`` fails the case (empty: it passes).

    A stated ``output`` must match exactly. Otherwise the output must keep what the API answered:
    raw bytes equal the reply; a parsed model keeps the reply's values (``lost_values``); a
    listing keeps the items of every page, in order. A result no reply lines up with must be
    stated, so nothing passes unchecked.

    Example:
        >>> case = Case(
        ...     "forms.me.get",
        ...     cli=None,
        ...     mcp=None,
        ...     exchanges=[(Sent("GET", "users/me"), Reply(json={"id": 4}))],
        ... )
        >>> output_problems(case, {"id": 4}), output_problems(case, {"id": None})
        ([], ['id: None != 4'])
    """
    if case.output is not UNSTATED:
        return [] if output == case.output else [f"returned {output!r}, stated {case.output!r}"]
    replies = [reply for _, reply in case.exchanges]
    if output is None:
        return []
    if isinstance(output, bytes):
        return [] if output == replies[-1].content else ["other bytes than the API sent"]
    if len(replies) == 1 and not isinstance(output, dict | list):
        return [] if output == replies[0].json else [f"{output!r} != {replies[0].json!r}"]
    if len(replies) == 1 and isinstance(output, dict) and isinstance(replies[0].json, dict):
        reply = replies[0].json
        if reply and not reply.keys() & output.keys():
            return ["kept no field of the reply; state the case's output"]
        return lost_values(output, reply)
    pages = [reply_items(reply.json) for reply in replies]
    if isinstance(output, list) and all(page is not None for page in pages):
        return lost_values(output, [item for page in pages for item in page or []])
    return ["no reply lines up with this result; state the case's output"]


def effect_sent(requests: Sequence[httpx2.Request]) -> Effect:
    """The strongest effect the endpoints behind ``requests`` declared."""
    return strongest(request.extensions[EFFECT_EXTENSION] for request in requests)


def hints_disagree(annotations: Mapping[str, Any], effect: Effect) -> list[str]:
    """The MCP hints in ``annotations`` that contradict ``effect`` (empty: they agree).

    Example:
        >>> hints_disagree(RO, "read")
        []
        >>> hints_disagree(WRITE, "idempotent_write")
        ['idempotentHint']
    """
    expected = EFFECT_HINTS[effect]
    return [key for key in HINT_KEYS if annotations.get(key) != expected.get(key)]


def load_cases() -> list[Case]:
    """Every resource's ``CASES``, from ``tests/yandex/<domain>/<resource>/cases.py``."""
    cases: list[Case] = []
    for path in sorted(TESTS.glob("yandex/*/*/cases.py")):
        module = ".".join(path.relative_to(TESTS.parent).with_suffix("").parts)
        cases += importlib.import_module(module).CASES
    return cases
