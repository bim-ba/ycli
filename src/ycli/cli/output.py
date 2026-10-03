"""CLI output rendering — commands return values, :func:`render` prints them in one place.

The root ``result_callback`` hands every command's return value to :func:`render`:
- a pydantic model goes through the ``--format`` strategy. stdout is data: when output is
  piped/redirected (not a TTY) the default ``auto`` stays raw JSON so scripts and agents keep a
  stable machine format; an interactive TTY gets a pretty table;
- ``--jq EXPR`` filters that model's JSON form through jq instead (:func:`render_jq`);
- a ``str`` or ``int`` prints verbatim (raw page markdown, a count);
- :class:`BinaryResult` writes bytes to a file or stdout;
- :class:`ExitWith` renders its result, then exits with a non-zero status;
- ``None`` prints nothing.

The MCP server never uses this module.
"""

from __future__ import annotations

# PEP 810: on Python 3.15+ these load on first use (only YAML and pretty output need them);
# older versions ignore the name.
__lazy_modules__ = {"yaml", "rich.table"}

import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from ycli.cli.exit_codes import ExitCode
from ycli.cli.formats import OutputFormat

if TYPE_CHECKING:
    from collections.abc import Iterator

# ``--jq`` prints JSON, so it cannot share a command line with a format that prints something else.
_NOT_JSON_FORMATS = frozenset({OutputFormat.yaml, OutputFormat.pretty})


class SerializationStrategy(ABC):
    """Prints a command result to a console; one subclass per ``--format`` choice."""

    @abstractmethod
    def render(self, result: BaseModel, console: Console) -> None:
        """Print ``result`` to ``console``."""

    @classmethod
    def from_format(cls, output_format: OutputFormat) -> SerializationStrategy:
        """Resolve a CLI ``--format`` choice to its strategy (no module-level registry)."""
        return {
            OutputFormat.json: JsonStrategy,
            OutputFormat.yaml: YamlStrategy,
            OutputFormat.pretty: PrettyStrategy,
            OutputFormat.auto: AutoStrategy,
        }[output_format]()


class JsonStrategy(SerializationStrategy):
    """``--format json``: highlighted on a terminal, one pristine line on a pipe."""

    def render(self, result: BaseModel, console: Console) -> None:
        """Print ``result`` as JSON."""
        text = result.model_dump_json(by_alias=True)
        if console.is_terminal:
            console.print_json(text)
        else:
            console.file.write(text + "\n")  # pristine, unwrapped JSON for pipes


class YamlStrategy(SerializationStrategy):
    """``--format yaml``: the model as block YAML."""

    def render(self, result: BaseModel, console: Console) -> None:
        """Print ``result`` as YAML."""
        data = result.model_dump(by_alias=True, mode="json")
        console.file.write(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


class PrettyStrategy(SerializationStrategy):
    """Render a model as a readable rich table — recursively, by structure, model-agnostic.

    Presentation only — the model layer already flattens API wrappers to scalars (see
    ``ycli.yandex.models`` ``KeyStr``/``IdStr``/``DisplayStr``), so this just lays data out:
    - a scalar renders as its text; a ``None`` / empty object / empty list field is *omitted*
      from the table (the data is unchanged — JSON/YAML still carry it);
    - an object becomes a key/value table; a *nested* object is flattened into dotted keys
      (``meta.owner``) rather than a sub-table, so a long value (email, id) keeps the full row
      width instead of a narrow inner column word-breaking it character-by-character;
    - a list of scalars joins with ``, ``; a list of objects becomes a column table whose
      all-empty columns are dropped.
    """

    def render(self, result: BaseModel, console: Console) -> None:
        """Print ``result`` as a table, or ``No results.`` when nothing is left to show."""
        rendered = self._render(result.model_dump(by_alias=True, mode="json"))
        console.print("[dim]No results.[/dim]" if rendered is None else rendered)

    def _render(self, value: Any) -> Any:
        """Value → a rich renderable (``str`` or ``Table``), or ``None`` to omit it."""
        if isinstance(value, dict):
            return self._render_object(value)
        if isinstance(value, list):
            return self._render_list(value)
        if value is None:
            return None
        if isinstance(value, bool):
            return "[green]✓[/]" if value else "[red]✗[/]"
        return escape(str(value))  # API text must not be parsed as rich markup

    def _render_object(self, data: dict[str, Any]) -> Any:
        rows = list(self._object_rows(data))
        if not rows:
            return None
        table = Table(show_header=False, box=None, pad_edge=False)
        table.add_column(style="cyan", no_wrap=True)
        table.add_column(overflow="fold")
        for key, rendered in rows:
            table.add_row(escape(key), rendered)
        return table

    def _object_rows(self, data: dict[str, Any], prefix: str = "") -> Iterator[tuple[str, Any]]:
        """Yield ``(dotted_key, renderable)`` rows, flattening nested objects one level deeper.

        Recursing on dict values (instead of rendering them as an inner table) means a nested
        ``{"owner": {"email": …}}`` becomes an ``owner.email`` row spanning the full width, so
        long identifier-like values are not shredded across lines by a narrow sub-column. A
        nested object that renders empty (all-null / ``{}``) yields no rows, so it stays omitted.
        """
        for key, value in data.items():
            dotted = f"{prefix}{key}"
            if isinstance(value, dict):
                yield from self._object_rows(value, prefix=f"{dotted}.")
            else:
                rendered = self._render(value)
                if rendered is not None:
                    yield dotted, rendered

    def _render_list(self, items: list[Any]) -> Any:
        rendered = [r for r in (self._render(item) for item in items) if r is not None]
        if not rendered:
            return None
        if all(isinstance(r, str) for r in rendered):
            return ", ".join(rendered)
        return self._render_object_list(items)

    def _render_object_list(self, items: list[Any]) -> Table:
        columns: list[str] = []
        for item in items:
            if isinstance(item, dict):
                columns.extend(key for key in item if key not in columns)
        cells = {
            column: [
                self._render(item.get(column)) if isinstance(item, dict) else None for item in items
            ]
            for column in columns
        }
        columns = [c for c in columns if any(value is not None for value in cells[c])]
        table = Table()
        for column in columns:
            table.add_column(escape(column), style="cyan", overflow="fold")
        for row in zip(*(cells[c] for c in columns), strict=True):
            table.add_row(*["" if value is None else value for value in row])
        return table


class AutoStrategy(SerializationStrategy):
    """``--format auto``: ``pretty`` on a terminal, ``json`` on a pipe."""

    def render(self, result: BaseModel, console: Console) -> None:
        """Print ``result`` with the strategy that fits ``console``."""
        (PrettyStrategy() if console.is_terminal else JsonStrategy()).render(result, console)


@dataclass(frozen=True)
class BinaryResult:
    """Raw bytes (an attachment, an export) for the file at ``path``, or stdout for ``None``/``-``.

    Bytes are not a model, so they are never JSON/YAML-serialized; stdout lets a shell redirect
    them (``ycli … > file``).
    """

    data: bytes
    path: str | None = None


@dataclass(frozen=True)
class ExitWith:
    """A result to render before exiting with ``exit_code`` (a report that says a check failed)."""

    result: BaseModel
    exit_code: int = 1


def check_jq(expression: str, output_format: OutputFormat) -> Any:
    """The compiled ``--jq`` program, or a usage error (exit 2) before a command has run.

    Fails early on a format that is not JSON, a missing ``jq`` extra and an expression that
    does not compile, so a bad filter never follows a write that already happened.
    """
    if output_format in _NOT_JSON_FORMATS:
        raise typer.BadParameter(
            f"--jq prints JSON; it cannot be combined with `--format {output_format}`.",
            param_hint="--jq",
        )
    try:
        import jq  # ty: ignore[unresolved-import]  # compiled, no stubs; lazy: loads only when used
    except ImportError as exc:
        raise typer.BadParameter(
            "it needs the `jq` extra: `uv tool install 'yandex-cli[jq]'` "
            "(or `pip install 'yandex-cli[jq]'`). The package has no build for every platform; "
            "without it, pipe the JSON output to the jq program.",
            param_hint="--jq",
        ) from exc
    try:
        return jq.compile(expression)
    except ValueError as exc:
        raise typer.BadParameter(f"not a valid jq program: {exc}", param_hint="--jq") from exc


def render_jq(result: BaseModel, expression: str, output_format: OutputFormat) -> None:
    """Print ``expression`` applied to the model's JSON form, one result per line, like ``jq -r``.

    A string result prints raw and anything else as compact JSON, so ``--jq .key`` prints a bare
    value. A runtime jq error (``.a.b`` on a number, ``error("x")``) exits 1 before printing.

    Example: ``.key, .n`` over ``{"key": "DE-1", "n": 3}`` prints ``DE-1`` then ``3``.
    """
    program = check_jq(expression, output_format)
    try:
        values = program.input_value(result.model_dump(by_alias=True, mode="json")).all()
    except ValueError as exc:
        typer.secho(f"Error: jq: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(ExitCode.FAILURE) from exc
    for value in values:
        print(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False))


def render(result: object, output_format: OutputFormat, jq: str | None = None) -> None:
    """Print a command's return value to stdout — the only place CLI output is produced.

    ``jq`` (``--jq``) filters a model's JSON form; a result that is not a model has none.
    """
    match result:
        case None:
            return
        case BaseModel() if jq is not None:
            render_jq(result, jq, output_format)
        case BaseModel():
            SerializationStrategy.from_format(output_format).render(result, Console())
        case str() | int() | BinaryResult() if jq is not None:
            raise typer.BadParameter(
                f"this command returns {type(result).__name__}, which has nothing to filter.",
                param_hint="--jq",
            )
        case str() | int():
            print(result)
        case BinaryResult(data=data, path=None | "-"):
            sys.stdout.buffer.write(data)
        case BinaryResult(data=data, path=str() as path):
            Path(path).write_bytes(data)
        case ExitWith(result=inner, exit_code=code):
            render(inner, output_format, jq)
            raise typer.Exit(code)
        case _:
            raise TypeError(f"a command returned {type(result).__name__}, which has no rendering")
