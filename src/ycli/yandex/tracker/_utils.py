"""Tracker CLI helpers — request-body builders and the ``--field key=value`` JSON coercer."""

from __future__ import annotations

import json
from typing import Any

import typer


def count_body(query: str = "", queue: str = "", status: str = "") -> dict[str, Any]:
    """Build the request body for ``POST /issues/_count``.

    When ``query`` is provided it takes precedence and the body is ``{"query": …}``.
    Otherwise a ``{"filter": {…}}`` body is built from the non-empty ``queue``/``status``
    values (an empty filter counts every issue in the org).

    Example:
        >>> count_body(query="Queue: DE")
        {'query': 'Queue: DE'}
        >>> count_body(queue="DE", status="open")
        {'filter': {'queue': 'DE', 'status': 'open'}}
        >>> count_body()
        {'filter': {}}
    """
    if query:
        return {"query": query}
    return {"filter": {k: v for k, v in (("queue", queue), ("status", status)) if v}}


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
