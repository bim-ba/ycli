"""ARCH-8 — Typed boundaries (see ARCHITECTURE.md)."""

from __future__ import annotations

import ast
import functools
from pathlib import Path

from tests.architecture.scanners import (
    SRC,
    YANDEX,
    _dotted,
    _import_aliases,
    violation_markers,
)

# ARCH-8 typed body (docs/conventions/resources.md §4 "Typed request body — never `dict`"): a
# `body` parameter is the resource's request model, never a bare `dict`/`dict[...]`, in every
# layer that hands it on: the MCP tool, the client method and the endpoint builder. Fail-closed;
# an exception would carry `# violation(arch-8): <reason>` above the function, and there is none.
# `Annotated[Base64Bytes, …]` (binary uploads) is an `ast.Subscript` whose `.value` is
# `ast.Name(id="Annotated")`, never `dict`, so it never matches this check.


def _bare_dict_annotation(annotation: ast.expr | None) -> bool:
    """``True`` if ``annotation`` is bare ``dict`` or subscripted ``dict[...]``.

    ``Annotated[Base64Bytes, …]`` is a subscript whose ``.value`` is ``ast.Name(id="Annotated")``
    — never ``"dict"`` — so it is never flagged.
    """
    if annotation is None:
        return False
    if isinstance(annotation, ast.Name):
        return annotation.id == "dict"
    return (
        isinstance(annotation, ast.Subscript)
        and isinstance(annotation.value, ast.Name)
        and annotation.value.id == "dict"
    )


def _bare_dict_bodies(source: str, module_label: str) -> list[tuple[int, str]]:
    """(line, finding) for ``@mcp.tool`` functions in ``source`` with a bare-``dict`` ``body``.

    The line is the first of the function's definition (its first decorator). Matches both
    ``def`` and ``async def`` tool functions, so a future async write tool cannot slip a
    bare-``dict`` ``body`` past the guard. Every positional-or-keyword and keyword-only parameter
    named ``body`` is checked.
    """
    found: list[tuple[int, str]] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(
            isinstance(deco, ast.Call)
            and isinstance(deco.func, ast.Attribute)
            and deco.func.attr == "tool"
            for deco in node.decorator_list
        ):
            continue
        first = min(deco.lineno for deco in node.decorator_list)
        found += [
            (
                first,
                f"{module_label}: {node.name}(body: {ast.unparse(arg.annotation)}) "
                "— must be a typed pydantic model, not dict",
            )
            for arg in (*node.args.args, *node.args.kwonlyargs)
            if arg.arg == "body"
            and arg.annotation is not None
            and _bare_dict_annotation(arg.annotation)
        ]
    return found


def _untyped_body_offenders(source: str, module_label: str) -> list[str]:
    """The :func:`_bare_dict_bodies` of ``source`` with no ``# violation(arch-8)`` above them.

    Pure over source text so the guard can be exercised on a synthetic module (the prove-it
    test).
    """
    markers = violation_markers(source, "arch-8")
    return [text for line, text in _bare_dict_bodies(source, module_label) if line not in markers]


def test_arch8_mcp_write_tool_bodies_are_typed():
    """A ``body`` parameter is a typed pydantic model, never bare ``dict``, in every layer.

    docs/conventions/resources.md §4: the model becomes the tool's input schema, so an agent
    sees field names/types/aliases instead of an opaque ``object``, and a malformed payload
    fails schema validation before the HTTP call. Fail-closed: only a function with
    ``# violation(arch-8): <reason>`` above it is exempt.
    """
    offenders = []
    for layer in ("mcp.py", "client.py", "endpoints.py"):
        for path in YANDEX.rglob(layer):
            rel = str(path.relative_to(SRC))
            offenders += _untyped_body_offenders(path.read_text(encoding="utf-8"), rel)
    assert not offenders, (
        "a `body` parameter must be a typed pydantic model, not dict — convert the parameter, "
        f"or put `# violation(arch-8): <reason>` above the function: {offenders}"
    )


def _dumps(source: str, module_label: str) -> list[str]:
    """Places in ``source`` that dump a model themselves (``.model_dump(`` / ``_json(``)."""
    return [
        f"{module_label}:{node.lineno}"
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"model_dump", "model_dump_json"}
    ]


def test_arch8_a_request_body_is_dumped_only_by_the_endpoint():
    """The MCP tool, the client and the endpoint builder hand the model on, undumped.

    ``Endpoint`` dumps it once (``Endpoint.body``), so every surface sends the same
    JSON. A CLI command may dump a model to merge ``--field`` values into it before it builds
    the request model.
    """
    offenders = []
    for layer in ("mcp.py", "client.py", "endpoints.py"):
        for path in YANDEX.rglob(layer):
            offenders += _dumps(path.read_text(encoding="utf-8"), str(path.relative_to(SRC)))
    assert offenders == []
    assert _dumps("def f(body):\n    return send(body.model_dump())\n", "x/client.py") == [
        "x/client.py:2"
    ]


def test_arch8_typed_body_guard_bites():
    """Prove-it: the guard flags bare/subscripted ``dict`` bodies and respects a marker.

    A typed model or ``Annotated[Base64Bytes, …]`` is not flagged.
    """
    bare = (
        '@mcp.tool(name="widgets_create")\n'
        "def create(body: dict, client=Depends(x)) -> Widget:\n"
        "    return client.widgets.create(body)\n"
    )
    assert _untyped_body_offenders(bare, "synthetic/mcp.py") == [
        "synthetic/mcp.py: create(body: dict) — must be a typed pydantic model, not dict"
    ]

    async_bare = (
        '@mcp.tool(name="widgets_create")\n'
        "async def create(body: dict, client=Depends(x)) -> Widget:\n"
        "    return await client.widgets.create(body)\n"
    )
    assert _untyped_body_offenders(async_bare, "synthetic/mcp.py") == [
        "synthetic/mcp.py: create(body: dict) — must be a typed pydantic model, not dict"
    ]

    subscripted = (
        '@mcp.tool(name="widgets_create")\n'
        "def create(body: dict[str, str], client=Depends(x)) -> Widget:\n"
        "    return client.widgets.create(body)\n"
    )
    assert _untyped_body_offenders(subscripted, "synthetic/mcp.py") == [
        "synthetic/mcp.py: create(body: dict[str, str]) — must be a typed pydantic model, not dict"
    ]

    typed = (
        '@mcp.tool(name="widgets_create")\n'
        "def create(body: WidgetCreate, client=Depends(x)) -> Widget:\n"
        "    return client.widgets.create(body)\n"
    )
    assert _untyped_body_offenders(typed, "synthetic/mcp.py") == []

    binary_upload = (
        '@mcp.tool(name="files_upload")\n'
        "def upload(body: Annotated[Base64Bytes, Field(...)], client=Depends(x)) -> Ack:\n"
        "    return client.files.upload(body)\n"
    )
    assert _untyped_body_offenders(binary_upload, "synthetic/mcp.py") == []

    marked = "# violation(arch-8): the API takes any object here\n" + bare
    assert _untyped_body_offenders(marked, "synthetic/mcp.py") == []


# Who may turn a status into a typed error, and why. ``raise_for_status``
# would bypass the mapping and raise a library error instead of a YandexError.
ARCH8_ERROR_MAPPERS = {
    Path("yandex/errors.py"): "defines error_for_status",
    Path("yandex/core/session.py"): "the httpx2 core sessions",
    Path("yandex/core/auth.py"): "the IAM token exchange outside the sessions",
    Path("yandex/status/client.py"): (
        "the OAuth login flow: a 400/401 with an OAuth error code is a device-flow polling "
        "state (RFC 6749 §5.2), not a failure for the session to raise"
    ),
}
# YandexError subclasses that carry no HTTP status: raising one maps no status.
ARCH8_STATUSLESS_ERRORS = {
    "YandexTimeoutError": "a local polling deadline (polling.poll)",
    "YandexConnectionError": "no HTTP response at all",
    "YandexInvalidRequestError": "a request of the wrong form, found before anything is sent",
    "YandexUnexpectedReplyError": "a reply that does not fit its model; no status is mapped",
}


@functools.cache
def _status_errors() -> frozenset[str]:
    """Every ``YandexError`` class in ``ycli.yandex.errors`` that stands for an HTTP status."""
    from ycli.yandex import errors

    defined = {
        name
        for name, value in vars(errors).items()
        if isinstance(value, type) and issubclass(value, errors.YandexError)
    }
    assert set(ARCH8_STATUSLESS_ERRORS) <= defined, "ARCH8_STATUSLESS_ERRORS names a gone class"
    return frozenset(defined - set(ARCH8_STATUSLESS_ERRORS))


def _error_mapping_offenders(rel: Path, source: str) -> list[str]:
    """Places in ``source`` that map an HTTP status by hand (import aliases resolved).

    Anywhere: ``raise_for_status``. Outside ``ARCH8_ERROR_MAPPERS``: any use of
    ``error_for_status``, building a status-carrying ``YandexError`` (``YandexNotFoundError(…)``)
    and reading a response's ``status_code``. Such an error may be built by hand only with
    ``# violation(arch-8): <reason>`` on the line above.
    """
    tree = ast.parse(source)
    aliases = _import_aliases(tree)
    mapper = rel in ARCH8_ERROR_MAPPERS
    marked = set(violation_markers(source, "arch-8"))
    offenders = []
    for top in tree.body:
        offenders += _mapping_offenders_in(top, rel, aliases, mapper=mapper, marked=marked)
    return offenders


def _hand_raises(source: str) -> list[int]:
    """The lines of ``source`` that build a status-carrying ``YandexError`` by hand."""
    tree = ast.parse(source)
    aliases = _import_aliases(tree)
    return sorted(
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and _dotted(node.func, aliases).rpartition(".")[2] in _status_errors()
    )


def _mapping_offenders_in(
    top: ast.stmt, rel: Path, aliases: dict[str, str], *, mapper: bool, marked: set[int]
) -> list[str]:
    """The :func:`_error_mapping_offenders` findings inside one top-level statement."""
    offenders = []
    for node in ast.walk(top):
        where = f"{rel}:{getattr(node, 'lineno', 0)}"
        if isinstance(node, ast.Attribute) and node.attr == "raise_for_status":
            offenders.append(f"{where}: raise_for_status bypasses errors.error_for_status")
        if mapper:
            continue
        if isinstance(node, ast.ImportFrom) and any(
            alias.name == "error_for_status" for alias in node.names
        ):
            offenders.append(f"{where}: imports error_for_status outside ARCH8_ERROR_MAPPERS")
        elif isinstance(node, ast.Name | ast.Attribute) and (
            _dotted(node, aliases).rpartition(".")[2] == "error_for_status"
        ):
            offenders.append(f"{where}: calls error_for_status outside ARCH8_ERROR_MAPPERS")
        elif isinstance(node, ast.Attribute) and node.attr == "status_code":
            offenders.append(f"{where}: reads status_code outside ARCH8_ERROR_MAPPERS")
        elif (
            isinstance(node, ast.Call)
            and node.lineno not in marked
            and (name := _dotted(node.func, aliases).rpartition(".")[2]) in _status_errors()
        ):
            offenders.append(f"{where}: raises {name} by hand instead of error_for_status")
    return offenders


def test_arch8_errors_are_mapped_in_one_place():
    """Non-2xx answers become typed YandexErrors through ``errors.error_for_status`` only."""
    offenders = [
        finding
        for p in SRC.rglob("*.py")
        for finding in _error_mapping_offenders(p.relative_to(SRC), p.read_text(encoding="utf-8"))
    ]
    assert not offenders, offenders


def test_arch8_error_mapping_guard_bites():
    session = Path("yandex/core/session.py")
    resource = Path("yandex/wiki/pages/client.py")
    assert _error_mapping_offenders(session, "response.raise_for_status()")
    for source in (
        "error_for_status(404, 'gone', url=u)",
        "from ycli.yandex.errors import error_for_status as efs\nraise efs(404, 'gone', url=u)",
        "from ycli.yandex import errors\nraise errors.error_for_status(404, 'gone', url=u)",
        "if response.status_code == 404:\n    raise LookupError(key)",
        "raise YandexNotFoundError('gone', status=404, url=u)",
        "from ycli.yandex.errors import YandexNotFoundError as Missing\nraise Missing('gone')",
        "raise errors.YandexError('failed', status=500)",
    ):
        assert _error_mapping_offenders(resource, source), source
    clean = (
        "raise YandexTimeoutError('late')\n"
        "try:\n    page = get(key)\nexcept YandexNotFoundError:\n    page = None\n"
        "hint = isinstance(error, YandexAuthError)\n"
    )
    assert _error_mapping_offenders(resource, clean) == []
    mapped = "raise error_for_status(response.status_code, message, url=u)"
    assert _error_mapping_offenders(session, mapped) == []
    # A marked local refusal may raise; the same raise with no marker may not.
    refusal = "def check_path(path):\n{}    raise YandexClientError(path)\n"
    endpoint = Path("yandex/core/endpoint.py")
    marker = "    # violation(arch-8): refused before any request is sent\n"
    assert _error_mapping_offenders(endpoint, refusal.format(marker)) == []
    assert _error_mapping_offenders(endpoint, refusal.format("")) == [
        "yandex/core/endpoint.py:2: raises YandexClientError by hand instead of error_for_status"
    ]


def _stale_markers(rel: str, source: str) -> list[str]:
    """``# violation(arch-8)`` markers of ``source`` above neither a hand-built error nor a body."""
    explained = set(_hand_raises(source)) | {line for line, _ in _bare_dict_bodies(source, rel)}
    return [
        f"{rel}:{marker}: violation(arch-8) marks nothing the checks find"
        for line, marker in sorted(violation_markers(source, "arch-8").items())
        if line not in explained
    ]


def test_arch8_a_marker_stands_above_what_it_explains():
    """Every ``# violation(arch-8)`` is above a hand-built status error or a ``dict`` body."""
    stale = [
        finding
        for path in sorted(SRC.rglob("*.py"))
        for finding in _stale_markers(str(path.relative_to(SRC)), path.read_text(encoding="utf-8"))
    ]
    assert stale == []
    marked = (
        "def check_path(path):\n"
        "    # violation(arch-8): refused before any request is sent\n"
        "    raise YandexClientError(path)\n"
    )
    assert _stale_markers("a/endpoint.py", marked) == []
    assert _stale_markers("a/endpoint.py", marked.replace("YandexClientError", "ValueError")) == [
        "a/endpoint.py:2: violation(arch-8) marks nothing the checks find"
    ]
