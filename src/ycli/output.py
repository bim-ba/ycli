"""CLI output rendering — one ``--format`` switch over pydantic results.

stdout is data: when output is piped/redirected (not a TTY) the default ``auto``
stays raw JSON so scripts and agents keep a stable machine format; an interactive
TTY gets a pretty table. Explicit ``--format json|yaml|pretty`` overrides that.
The MCP server never uses this module.
"""

from __future__ import annotations

import enum
import json
import re
from typing import Any

import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table


_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")


def _key_link(value: str) -> str:
    """Wrap a Tracker issue key in a rich OSC8 link to its web UI page."""
    return f"[link=https://tracker.yandex.ru/{value}]{value}[/link]"


class OutputFormat(str, enum.Enum):
    """CLI ``--format`` choices."""

    auto = "auto"
    json = "json"
    yaml = "yaml"
    pretty = "pretty"


_format: OutputFormat = OutputFormat.auto


def set_format(fmt: OutputFormat) -> None:
    """Record the global ``--format`` choice (set once by the root CLI callback)."""
    global _format
    _format = fmt


def render(result: BaseModel, *, console: Console | None = None) -> None:
    """Print ``result`` in the active format.

    ``auto`` (the default) renders a pretty table on a TTY and raw JSON when piped,
    keeping stdout machine-readable for scripts and agents.
    """
    console = console or Console()
    fmt = _format
    if fmt is OutputFormat.auto:
        fmt = OutputFormat.pretty if console.is_terminal else OutputFormat.json

    if fmt is OutputFormat.json:
        text = result.model_dump_json(by_alias=True)
        if console.is_terminal:
            console.print_json(text)
        else:
            console.file.write(text + "\n")  # pristine, unwrapped JSON for pipes
    elif fmt is OutputFormat.yaml:
        data = result.model_dump(by_alias=True, mode="json")
        console.file.write(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    else:  # pretty
        console.print(_prettify(result.model_dump(by_alias=True, mode="json"), link=console.is_terminal))


def _prettify(data: Any, *, link: bool = False) -> Any:
    """Turn a JSON-able structure into a rich renderable (table) or plain string."""
    if isinstance(data, list):
        return _list_table(data, link=link)
    if isinstance(data, dict):
        return _kv_table(data, link=link)
    return str(data)


def _kv_table(data: dict[str, Any], *, link: bool = False) -> Table:
    """A single object → a two-column field/value table."""
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(overflow="fold")
    for key, value in data.items():
        table.add_row(str(key), _cell(value, is_key=(key == "key"), link=link))
    return table


def _list_table(items: list[Any], *, link: bool = False) -> Table:
    """A list → a table: a column per field for dict items, else one value column."""
    table = Table()
    if items and isinstance(items[0], dict):
        columns = list(items[0].keys())
        for column in columns:
            table.add_column(str(column), style="cyan", overflow="fold")
        for item in items:
            table.add_row(*[_cell(item.get(column), is_key=(column == "key"), link=link) for column in columns])
    else:
        table.add_column("value", overflow="fold")
        for item in items:
            table.add_row(_cell(item, link=link))
    return table


def _cell(value: Any, *, is_key: bool = False, link: bool = False) -> str:
    """Render one cell: nested structures as compact JSON, ``None`` as empty; a Tracker key links on a TTY."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    text = str(value)
    if link and is_key and _KEY_RE.match(text):
        return _key_link(text)
    return text
