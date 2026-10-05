"""Shared CLI helper — the ``key=value`` field parser behind ``--field`` and ``ycli api -f/-F``."""

import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import typer

_KEY = re.compile(r"(?P<name>[^\[\]]+)(?P<brackets>(?:\[[^\[\]]*\])*)")
_BRACKET = re.compile(r"\[([^\[\]]*)\]")


def parse_fields(
    items: list[str] | None = None,
    *,
    raw: list[str] | None = None,
    structured: bool = False,
    nested: bool = False,
) -> dict[str, Any]:
    """Parse repeated ``key=value`` strings into a dict (the gh ``-F`` / ``-f`` model).

    ``items`` are typed: each value is JSON-coerced (``123`` → int, ``true`` → bool,
    ``{"id":5}`` → object), falling back to the raw string when it is not valid JSON (``NaN``,
    ``Infinity`` and ``1e999`` are not: JSON has no such numbers). ``raw``
    values are always strings and are applied first. ``structured`` adds what ``ycli api``
    needs: ``key[sub]=v`` nests, ``key[]=v`` appends to an array, and a typed value ``@file``
    (``@-`` for stdin) is the file's text; ``nested`` adds the keys alone, without ``@file``.
    Raises ``typer.BadParameter`` for an item without
    ``=``, a malformed key, a missing file or a key that clashes with an earlier one.

    Args:
        items: Typed ``key=value`` strings.
        raw: Always-string ``key=value`` strings, applied first.
        structured: Whether ``key[sub]``, ``key[]`` and ``@file`` values are understood.
        nested: Whether ``key[sub]`` and ``key[]`` are understood (a value stays as given).

    Returns:
        The parsed fields.

    Examples:
        >>> parse_fields(["sprint=123", "name=hi"])
        {'sprint': 123, 'name': 'hi'}
        >>> parse_fields(["a[b]=true", "t[]=1", "t[]=2"], raw=["id=7"], structured=True)
        {'id': '7', 'a': {'b': True}, 't': [1, 2]}
    """
    out: dict[str, Any] = {}
    for item in raw or []:
        key, text = _pair(item)
        _assign(out, key, text, structured=structured or nested)
    for item in items or []:
        key, text = _pair(item)
        _assign(out, key, _typed(text, structured=structured), structured=structured or nested)
    return out


def _pair(item: str) -> tuple[str, str]:
    key, sep, text = item.partition("=")
    if not sep:
        raise typer.BadParameter(f"a field must be key=value, got {item!r}")
    return key, text


def _typed(text: str, *, structured: bool) -> Any:
    if structured and text.startswith("@"):
        return _read_text(text[1:])
    try:
        return json.loads(text, parse_float=_finite, parse_constant=_finite)
    except ValueError:  # not JSON, or a number JSON cannot carry: the text as written
        return text


def _finite(text: str) -> float:
    """``text`` as a number; ``NaN``, ``Infinity`` and an overflow like ``1e999`` are not one."""
    number = float(text)
    if not math.isfinite(number):
        raise ValueError(text)
    return number


def _read_text(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    try:
        return Path(source).read_text(encoding="utf-8")
    except OSError as exc:
        raise typer.BadParameter(f"cannot read {source!r}: {exc.strerror}") from exc


def _assign(out: dict[str, Any], key: str, value: Any, *, structured: bool) -> None:
    """Set ``out[key]``; in a structured key ``a[b][]`` walks into ``out["a"]["b"]`` and appends."""
    if not structured:
        out[key] = value
        return
    match = _KEY.fullmatch(key)
    path = [match["name"], *_BRACKET.findall(match["brackets"])] if match else []
    if not path or "" in path[:-1]:
        raise typer.BadParameter(f"not a valid field name: {key!r}")
    append = path[-1] == ""
    *parents, last = path[:-1] if append else path
    node = out
    for step in parents:
        node = node.setdefault(step, {})
        if not isinstance(node, dict):
            raise typer.BadParameter(f"field {key!r} clashes with an earlier field")
    if append:
        items = node.setdefault(last, [])
        if not isinstance(items, list):
            raise typer.BadParameter(f"field {key!r} clashes with an earlier field")
        items.append(value)
    elif isinstance(node.get(last), dict | list):
        raise typer.BadParameter(f"field {key!r} clashes with an earlier field")
    else:
        node[last] = value
