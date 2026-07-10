"""CLI output rendering — one ``--format`` switch over pydantic results.

stdout is data: when output is piped/redirected (not a TTY) the default ``auto``
stays raw JSON so scripts and agents keep a stable machine format; an interactive
TTY gets a pretty table. Explicit ``--format json|yaml|pretty`` overrides that.
The MCP server never uses this module.
"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import yaml
from rich.table import Table

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pydantic import BaseModel
    from rich.console import Console


class OutputFormat(enum.StrEnum):
    """CLI ``--format`` choices."""

    auto = "auto"
    json = "json"
    yaml = "yaml"
    pretty = "pretty"


class SerializationStrategy(ABC):
    @abstractmethod
    def render(self, result: BaseModel, console: Console) -> None: ...

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
    def render(self, result: BaseModel, console: Console) -> None:
        text = result.model_dump_json(by_alias=True)
        if console.is_terminal:
            console.print_json(text)
        else:
            console.file.write(text + "\n")  # pristine, unwrapped JSON for pipes


class YamlStrategy(SerializationStrategy):
    def render(self, result: BaseModel, console: Console) -> None:
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
        return str(value)

    def _render_object(self, data: dict[str, Any]) -> Any:
        rows = list(self._object_rows(data))
        if not rows:
            return None
        table = Table(show_header=False, box=None, pad_edge=False)
        table.add_column(style="cyan", no_wrap=True)
        table.add_column(overflow="fold")
        for key, rendered in rows:
            table.add_row(key, rendered)
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
            table.add_column(column, style="cyan", overflow="fold")
        for row in zip(*(cells[c] for c in columns), strict=True):
            table.add_row(*["" if value is None else value for value in row])
        return table


class AutoStrategy(SerializationStrategy):
    def render(self, result: BaseModel, console: Console) -> None:
        (PrettyStrategy() if console.is_terminal else JsonStrategy()).render(result, console)


class Serializer:
    """The single serialization dispatch point — applies a chosen strategy to a model."""

    @staticmethod
    def serialize(model: BaseModel, strategy: SerializationStrategy, console: Console) -> None:
        strategy.render(model, console)
