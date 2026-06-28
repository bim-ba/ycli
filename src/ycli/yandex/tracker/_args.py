"""Shared tracker CLI arg types + the ``--field key=value`` JSON-coerce helper."""

from __future__ import annotations

import json
from typing import Annotated, Any

import typer

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key, e.g. DATAENGINEERING-1.")]


def parse_fields(items: list[str] | None) -> dict[str, Any]:
    """Parse repeated ``--field key=value`` strings into a dict (gh ``-F`` model).

    Each value is JSON-coerced (``123`` → int, ``true`` → bool, ``{"id":5}`` → object),
    falling back to the raw string when it is not valid JSON. Raises ``typer.BadParameter``
    when an item has no ``=``.

    Example:
        >>> parse_fields(["sprint=123", "name=hi"])
        {'sprint': 123, 'name': 'hi'}
    """
    out: dict[str, Any] = {}
    for item in items or []:
        key, sep, raw = item.partition("=")
        if not sep:
            raise typer.BadParameter(f"--field must be key=value, got {item!r}")
        try:
            out[key] = json.loads(raw)
        except json.JSONDecodeError:
            out[key] = raw
    return out
