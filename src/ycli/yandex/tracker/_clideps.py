"""Lazy Typer DI for the tracker CLI + the ``--field key=value`` JSON-coerce helper."""
from __future__ import annotations

import json
from typing import Any

import typer

from ycli.yandex.tracker.client import TrackerClient


def tracker_client(ctx: typer.Context) -> TrackerClient:
    """Return the request-scoped TrackerClient, building it from env on first access.

    Lazy so ``--help`` (which never runs a command body) needs no creds; cached on
    ``ctx.obj`` so multiple accesses within one invocation share the session.

    Example:
        >>> tracker_client(ctx)  # doctest: +SKIP
    """
    if ctx.obj is None:
        ctx.obj = TrackerClient.from_env()
    return ctx.obj


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
