"""``-F`` and ``--body-file`` — any field of a request body, on every command that sends one.

Both are global options (:mod:`ycli.cli.global_options`). :class:`CallerFields` reads them from
the root state once per invocation and lays them under a body: the file first, ``-F`` over it,
what the command built from its flags over both. :class:`~ycli.cli.guard.SendGuard` does that to
the first request a command sends; a command whose body must pass a model first (a union that
picks its class by a field) asks for the :class:`CallerFields` itself and merges before it
validates.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
from pydantic import JsonValue, TypeAdapter

from ycli.cli.fields import parse_fields

if TYPE_CHECKING:
    from collections.abc import Mapping


_OBJECT: TypeAdapter[dict[str, JsonValue]] = TypeAdapter(dict[str, JsonValue])


def laid_under(body: dict[str, Any], under: Mapping[str, Any]) -> dict[str, Any]:
    """``body`` with the fields of ``under`` it does not set itself, object by object.

    Args:
        body: The body a command built; its values win.
        under: The fields to add where ``body`` has none.

    Returns:
        The merged body.

    Examples:
        >>> laid_under({"name": "A", "fields": {"x": 1}}, {"name": "B", "fields": {"y": 2}})
        {'name': 'A', 'fields': {'y': 2, 'x': 1}}
    """
    merged = dict(under)
    for key, value in body.items():
        below = merged.get(key)
        both_objects = isinstance(value, dict) and isinstance(below, dict)
        merged[key] = laid_under(value, below) if both_objects else value
    return merged


def _read(body_file: Path) -> dict[str, Any]:
    """The object in ``body_file``: YAML by a ``.yaml`` / ``.yml`` name, JSON by any other.

    It goes through pydantic either way: a file that holds no object, or a YAML value JSON has
    no form for (a date), is a ValidationError, which the CLI prints like any other body that
    cannot be built.
    """
    held = _parsed(body_file)
    if not _finite(held):
        raise typer.BadParameter(
            "the file holds a number JSON cannot carry (NaN, Infinity)", param_hint="--body-file"
        )
    return held


def _parsed(body_file: Path) -> dict[str, Any]:
    """What :func:`_read` reads, before its numbers are checked."""
    if body_file.suffix.lower() not in {".yaml", ".yml"}:
        return _OBJECT.validate_json(body_file.read_bytes())
    import yaml  # here: only this branch needs it, and every invocation loads this module

    try:
        documents = list(yaml.safe_load_all(body_file.read_bytes()))
    except yaml.YAMLError as exc:
        raise typer.BadParameter(f"not YAML: {exc}", param_hint="--body-file") from exc
    if len(documents) != 1:
        raise typer.BadParameter(
            f"a body is one YAML document, the file holds {len(documents)}",
            param_hint="--body-file",
        )
    return _OBJECT.validate_python(documents[0])


def _finite(value: object) -> bool:
    """Whether every number in ``value`` is one JSON can carry: no ``NaN``, no ``Infinity``."""
    if isinstance(value, dict | list):
        return all(map(_finite, value.values() if isinstance(value, dict) else value))
    return not isinstance(value, float) or math.isfinite(value)


@dataclass
class CallerFields:
    """What ``--body-file`` and ``-F`` gave in this invocation; ``options`` is the root state.

    ``options`` is read when the fields are first asked for, so an option given after the
    subcommand counts. They go into one body only: :attr:`taken` says they already have.
    """

    options: Mapping[str, Any]
    taken: bool = False

    @property
    def given(self) -> bool:
        """Whether either option was given."""
        return bool(self.options.get("field")) or self.options.get("body_file") is not None

    def over(self, body: dict[str, Any]) -> dict[str, Any]:
        """``body`` over the caller's fields: the file, ``-F`` over it, ``body`` over both.

        Args:
            body: What the command built from its flags.

        Returns:
            The body to send.

        Examples:
            >>> CallerFields({"field": ["a[b]=1", "name=F"]}).over({"name": "flag"})
            {'a': {'b': 1}, 'name': 'flag'}
        """
        self.taken = True
        body_file = self.options.get("body_file")
        from_file = _read(Path(body_file)) if body_file else {}
        from_fields = parse_fields(self.options.get("field"), structured=True)
        return laid_under(body, laid_under(from_fields, from_file))
