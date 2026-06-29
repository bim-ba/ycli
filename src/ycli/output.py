"""CLI output rendering — one ``--format`` switch over pydantic results.

stdout is data: when output is piped/redirected (not a TTY) the default ``auto``
stays raw JSON so scripts and agents keep a stable machine format; an interactive
TTY gets a pretty table. Explicit ``--format json|yaml|pretty`` overrides that.
The MCP server never uses this module.
"""

from __future__ import annotations

import enum
import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import yaml
from rich.table import Table

if TYPE_CHECKING:
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


class RichCell:
    """A single rendered cell: value → display text."""

    def __init__(self, text: str) -> None:
        self.text = text

    @classmethod
    def of(cls, value: Any) -> RichCell:
        if isinstance(value, (dict, list)):
            return cls(json.dumps(value, ensure_ascii=False))
        if value is None:
            return cls("")
        return cls(str(value))


class PrettyStrategy(SerializationStrategy):
    def render(self, result: BaseModel, console: Console) -> None:
        console.print(self._prettify(result.model_dump(by_alias=True, mode="json")))

    def _prettify(self, data: Any) -> Any:
        if isinstance(data, list):
            return self._list_table(data)
        if isinstance(data, dict):
            return self._kv_table(data)
        return str(data)

    def _kv_table(self, data: dict[str, Any]) -> Table:
        table = Table(show_header=False, box=None, pad_edge=False)
        table.add_column(style="cyan", no_wrap=True)
        table.add_column(overflow="fold")
        for key, value in data.items():
            table.add_row(str(key), RichCell.of(value).text)
        return table

    def _list_table(self, items: list[Any]) -> Table:
        if items and isinstance(items[0], dict):
            return self._list_of_dicts_table(items)
        return self._list_of_scalars_table(items)

    def _list_of_dicts_table(self, items: list[dict[str, Any]]) -> Table:
        table = Table()
        columns = list(items[0].keys())
        for column in columns:
            table.add_column(str(column), style="cyan", overflow="fold")
        for item in items:
            table.add_row(*[RichCell.of(item.get(c)).text for c in columns])
        return table

    def _list_of_scalars_table(self, items: list[Any]) -> Table:
        table = Table()
        table.add_column("value", overflow="fold")
        for item in items:
            table.add_row(RichCell.of(item).text)
        return table


class AutoStrategy(SerializationStrategy):
    def render(self, result: BaseModel, console: Console) -> None:
        (PrettyStrategy() if console.is_terminal else JsonStrategy()).render(result, console)


class Serializer:
    """The single serialization dispatch point — applies a chosen strategy to a model."""

    @staticmethod
    def serialize(model: BaseModel, strategy: SerializationStrategy, console: Console) -> None:
        strategy.render(model, console)
