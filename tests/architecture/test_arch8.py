"""ARCH-8 — Typed boundaries (see ARCHITECTURE.md)."""

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

# A `body` parameter is a request model, never a `dict`, in the tool, the client method and the
# endpoint builder alike: the ast-grep rule `body-is-a-model` (.ast-grep/rules/) checks the text
# of each, with its own cases beside it.


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
    "YandexNotConfiguredError": "a service the credentials cannot reach; nothing is sent",
    "YandexUnexpectedReplyError": "a reply that does not fit its model; no status is mapped",
    "YandexDeclinedError": "an operation nobody confirmed; nothing is sent",
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
    """``# violation(arch-8)`` markers of ``source`` that stand above no hand-built error."""
    explained = set(_hand_raises(source))
    return [
        f"{rel}:{marker}: violation(arch-8) marks nothing the checks find"
        for line, marker in sorted(violation_markers(source, "arch-8").items())
        if line not in explained
    ]


def test_arch8_a_marker_stands_above_what_it_explains():
    """Every ``# violation(arch-8)`` is above a hand-built status error."""
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
