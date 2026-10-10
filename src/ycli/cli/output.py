"""CLI output rendering — commands return values, :func:`render` prints them in one place.

The root ``result_callback`` hands every command's return value to :func:`render`:
- a pydantic model goes through the ``--format`` strategy. stdout is data: when output is
  piped/redirected (not a TTY) the default ``auto`` stays raw JSON so scripts and agents keep a
  stable machine format; an interactive TTY gets a pretty table. ``csv`` and ``markdown`` print
  a table whose columns are the fields the model declares, ``ndjson`` one item on a line;
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

import csv
import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from types import NoneType, UnionType
from typing import TYPE_CHECKING, Annotated, Any, Union, get_args, get_origin

import typer
import yaml
from pydantic import BaseModel, RootModel
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from ycli.cli.formats import OutputFormat
from ycli.yandex.core.listing import Listing
from ycli.yandex.errors import YandexUnexpectedReplyError
from ycli.yandex.models import ItemList, Listed
from ycli.yandex.sync.marks import Identity

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


class SerializationStrategy(ABC):
    """Prints a command result to a console; one subclass per ``--format`` choice."""

    def __init__(self, declared: object = None) -> None:
        #: What the command says it returns, where the result is that.
        self.declared = declared

    @abstractmethod
    def render(self, result: BaseModel, console: Console) -> None:
        """Print ``result`` to ``console``."""

    def render_listing(self, listed: Listed[Any], console: Console) -> None:
        """Print a listing as the MCP tool and the SDK give it: ``{items, truncated, next, total}``.

        A structural format prints the result as it is (#538); a table overrides this and
        prints the rows alone.
        """
        self.render(listed, console)

    @classmethod
    def from_format(
        cls, output_format: OutputFormat, declared: object = None
    ) -> SerializationStrategy:
        """Resolve a CLI ``--format`` choice to its strategy (no module-level registry)."""
        return {
            OutputFormat.json: JSONStrategy,
            OutputFormat.yaml: YAMLStrategy,
            OutputFormat.pretty: PrettyStrategy,
            OutputFormat.auto: AutoStrategy,
            OutputFormat.csv: CSVStrategy,
            OutputFormat.markdown: MarkdownStrategy,
            OutputFormat.ndjson: NDJSONStrategy,
            OutputFormat.name: NameStrategy,
        }[output_format](declared)


class JSONStrategy(SerializationStrategy):
    """``--format json``: highlighted on a terminal, one pristine line on a pipe."""

    def render(self, result: BaseModel, console: Console) -> None:
        """Print ``result`` as JSON."""
        text = result.model_dump_json(by_alias=True)
        if console.is_terminal:
            console.print_json(text)
        else:
            console.file.write(text + "\n")  # pristine, unwrapped JSON for pipes


class YAMLStrategy(SerializationStrategy):
    """``--format yaml``: the model as block YAML."""

    def render(self, result: BaseModel, console: Console) -> None:
        """Print ``result`` as YAML."""
        data = result.model_dump(by_alias=True, mode="json")
        console.file.write(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


class PrettyStrategy(SerializationStrategy):
    """Render a model as a readable rich table — recursively, by structure, model-agnostic.

    Presentation only — the model layer already flattens API wrappers to scalars (see
    ``ycli.yandex.models`` ``KeyStr``/``IDStr``/``DisplayStr``), so this just lays data out:
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

    def render_listing(self, listed: Listed[Any], console: Console) -> None:
        """Print the rows: a table has no room for the envelope; where it stopped goes to stderr."""
        self.render(ItemList[Any](listed.items), console)

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
        self._fitting(console).render(result, console)

    def render_listing(self, listed: Listed[Any], console: Console) -> None:
        """Print ``listed`` with the strategy that fits ``console``."""
        self._fitting(console).render_listing(listed, console)

    @staticmethod
    def _fitting(console: Console) -> SerializationStrategy:
        return PrettyStrategy() if console.is_terminal else JSONStrategy()


def _unwrapped(value: object) -> object:
    """What a root model holds, so a result that wraps one object is that object."""
    while isinstance(value, RootModel):
        value = value.root
    return value


def _items(result: BaseModel) -> list[tuple[type, Any]]:
    """The rows of a result, each with its class and as JSON carries it, under the API's keys.

    The rows are the items of a listing, or the one object the result is.
    """
    held = result.items if isinstance(result, Listed) else _unwrapped(result)
    data = result.model_dump(by_alias=True, mode="json")
    if isinstance(result, Listed):
        data = data["items"]
    if not isinstance(held, list):
        held, data = [held], [data]
    return [(type(_unwrapped(item)), dumped) for item, dumped in zip(held, data, strict=True)]


def _compact(value: Any) -> str:
    """``value`` as one line of JSON, the text ``-o json`` prints on a pipe."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class NDJSONStrategy(SerializationStrategy):
    """``--format ndjson``: one item on a line; a result that is one object is one line.

    Only the items are printed: where a listing stopped is said on stderr, so every line
    parses the same way.
    """

    def render(self, result: BaseModel, console: Console) -> None:
        """Print each item of ``result`` as a line of JSON."""
        console.file.writelines(_compact(item) + "\n" for _, item in _items(result))


#: The path of a column inside an item, by the API's keys; the empty path is the item itself.
type _Column = tuple[str, ...]


def _nested(annotation: object) -> type[BaseModel] | None:
    """The one model a field holds (``Status`` or ``Status | None``), if it holds just that."""
    origin = get_origin(annotation)
    if origin is Annotated:
        return _nested(get_args(annotation)[0])
    if origin in (Union, UnionType):
        held = [kind for kind in get_args(annotation) if kind is not NoneType]
        return _nested(held[0]) if len(held) == 1 else None
    plain = isinstance(annotation, type) and issubclass(annotation, BaseModel)
    return annotation if plain and not issubclass(annotation, RootModel) else None


def _kinds(declared: object, *, item: bool = False) -> Iterator[type]:
    """The classes of the rows a command says it returns: ``Listing[Board]`` → ``Board``.

    A listing of several kinds names each. What is not a model is a row only as an item of a
    listing (``Listing[str]``); a result that is no model has no table.
    """
    origin = get_origin(declared)
    if origin is Annotated:
        yield from _kinds(get_args(declared)[0], item=item)
    elif origin in (Union, UnionType):
        for kind in get_args(declared):
            yield from _kinds(kind, item=item)
    elif origin in (Listing, list):
        yield from _kinds(get_args(declared)[0], item=True)
    elif isinstance(declared, type) and issubclass(declared, RootModel):
        yield from _kinds(declared.model_fields["root"].annotation, item=item)
    elif isinstance(declared, type) and issubclass(declared, Listed):
        yield from _kinds(declared.model_fields["items"].annotation, item=item)
    else:
        kind = origin or declared
        if (
            isinstance(kind, type)
            and kind is not NoneType
            and (item or issubclass(kind, BaseModel))
        ):
            yield kind


def _columns(model: type[BaseModel], above: tuple[type[BaseModel], ...] = ()) -> Iterator[_Column]:
    """The columns a model declares: a nested object is laid out as ``status.key``.

    A list, a mapping and a model that holds itself stay one column, printed as JSON text.
    """
    if not model.model_fields:
        yield ()  # nothing declared: the object is one cell
        return
    for name, field in model.model_fields.items():
        key = field.serialization_alias or field.alias or name
        nested = _nested(field.annotation)
        if nested is None or nested in above or nested is model:
            yield (key,)
        else:
            yield from ((key, *rest) for rest in _columns(nested, (*above, model)))


def _cell(item: Any, column: _Column) -> str:
    """The text of one cell: a scalar as it is, a list or an object as JSON text."""
    value = item
    for key in column:
        value = value.get(key) if isinstance(value, dict) else None
    if value is None:
        return ""
    return value if isinstance(value, str) else _compact(value)


class TableStrategy(SerializationStrategy):
    """A table whose columns are the fields the model declares, so data does not move them.

    A result that is one object is a table of one row. A field the service added and the
    model does not declare has no column; ``-o json`` prints it.
    """

    def render(self, result: BaseModel, console: Console) -> None:
        """Print ``result`` as a header and one row for each item."""
        items = _items(result)
        columns: list[_Column] = []
        # The declared kinds first: the header is the same whatever the reply holds, if anything.
        for kind in dict.fromkeys([*_kinds(self.declared), *(kind for kind, _ in items)]):
            declared = _columns(kind) if issubclass(kind, BaseModel) else [()]
            columns.extend(column for column in declared if column not in columns)
        if not columns:
            return
        header = [".".join(column) or "value" for column in columns]
        rows = [[_cell(item, column) for column in columns] for _, item in items]
        self.write(header, rows, console)

    @abstractmethod
    def write(self, header: Sequence[str], rows: Sequence[Sequence[str]], console: Console) -> None:
        """Print the header and the rows of cells."""


class CSVStrategy(TableStrategy):
    """``--format csv``: RFC 4180 quoting, UTF-8 with no byte order mark, cells as they came.

    A cell is the service's text unchanged, so one that starts with ``=`` is a formula to a
    spreadsheet that opens the file.
    """

    def write(self, header: Sequence[str], rows: Sequence[Sequence[str]], console: Console) -> None:
        """Print the table as CSV."""
        csv.writer(console.file, lineterminator="\n").writerows([header, *rows])


class MarkdownStrategy(TableStrategy):
    """``--format markdown``: a pipe table; ``|`` and a line break inside a cell are escaped."""

    def write(self, header: Sequence[str], rows: Sequence[Sequence[str]], console: Console) -> None:
        """Print the table as Markdown."""
        lines = [header, ["---"] * len(header), *([self._escaped(c) for c in row] for row in rows)]
        console.file.writelines(f"| {' | '.join(line)} |\n" for line in lines)

    @staticmethod
    def _escaped(cell: str) -> str:
        return cell.replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>")


def _identifier(kind: type) -> _Column | None:
    """The column that names an object of ``kind``: its one field marked ``Identity()``.

    What is not an object (a tag, a number) is its own name.
    """
    if not issubclass(kind, BaseModel):
        return ()
    marked = [
        (field.serialization_alias or field.alias or name,)
        for name, field in kind.model_fields.items()
        if any(isinstance(mark, Identity) for mark in field.metadata)
    ]
    return marked[0] if len(marked) == 1 else None


def has_names(declared: object) -> bool:
    """Whether ``-o name`` can print what a command says it returns.

    Args:
        declared: The return type the command declares.

    Returns:
        Whether every kind of row it returns has a field that names it.

    Examples:
        >>> from ycli.yandex.models import Ack
        >>> has_names(Listing[str]), has_names(Listing[Ack]), has_names(None)
        (True, False, False)
    """
    kinds = list(_kinds(declared))
    return bool(kinds) and all(_identifier(kind) is not None for kind in kinds)


class NameStrategy(SerializationStrategy):
    """``--format name``: the identifier of each item on a line, what the read command takes.

    ``ycli tracker issues search … -o name | xargs -n1 ycli tracker issues get``. An object
    inside another one prints its own identifier, not its parent's; a reply that
    left the identifier of an item out is an error, and nothing is printed. A command whose result
    has no name is refused before it sends anything; a result that is not what the command
    declares (the plan of ``--dry-run``) is printed as JSON.
    """

    def render(self, result: BaseModel, console: Console) -> None:
        """Print the identifier of each item of ``result`` on its own line.

        Args:
            result: What the command returned.
            console: Where to print.

        Raises:
            YandexUnexpectedReplyError: The reply left the identifier of an item out; nothing
                is printed, so a script does not act on fewer objects than were listed.
        """
        items = _items(result)
        columns = [_identifier(kind) for kind, _ in items]
        if None in columns:
            JSONStrategy().render(result, console)
            return
        names = [
            _cell(item, column)
            for (_, item), column in zip(items, columns, strict=True)
            if column is not None
        ]
        unnamed = [number for number, name in enumerate(names, start=1) if not name]
        if unnamed:
            first = unnamed[0]
            more = f" (and {len(unnamed) - 1} more)" if len(unnamed) > 1 else ""
            key = ".".join(columns[first - 1] or ())
            raise YandexUnexpectedReplyError(
                f"item {first} of this listing has no {key}{more}: `-o name` cannot name it. "
                "The request was sent: a command that changes something has changed it"
            )
        console.file.writelines(name + "\n" for name in names)


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


@dataclass(frozen=True)
class Continuable:
    """A listing, and the command line that goes on with it once ``--next`` is put after it."""

    listing: Listing[Any]
    command: str


@dataclass(frozen=True)
class Declared:
    """What a command returned, and what it says it returns: a table takes its columns from that.

    So an empty listing has a header too, and a listing of several kinds has the columns of each
    whatever the reply held.
    """

    result: object
    returns: object


def render(result: object, output_format: OutputFormat, declared: object = None) -> None:
    """Print a command's return value to stdout — the only place CLI output is produced.

    Args:
        result: What the command returned.
        output_format: The ``--format`` choice.
        declared: What the command says it returns, where ``result`` is that.

    Raises:
        TypeError: The command returned a value that has no rendering.
        typer.Exit: After an :class:`ExitWith` is printed, with its exit code.
    """
    match result:
        case None:
            return
        case Declared(result=inner, returns=returns):
            render(inner, output_format, returns)
        case Continuable(listing=listing, command=command):
            # What it gave, as the format shows a listing; where it stopped is said on stderr.
            listed = listing.collect()
            SerializationStrategy.from_format(output_format, declared).render_listing(
                listed, Console()
            )
            if listed.truncated:
                # It stopped at the limit; whether anything is left only the next call can say.
                of = "" if listed.total is None else f" of {listed.total}"
                # Counted over the calls this one went on from: a piece is not the whole.
                shown = f"stopped at {listing.seen}{of}"
                # A line to run as it is: the command with what it cannot be called without.
                hint = f"{shown}; go on with: {command} --next {listed.next}  (or --all)"
                typer.echo(hint, err=True)
        case BaseModel():
            SerializationStrategy.from_format(output_format, declared).render(result, Console())
        case str() | int():
            print(result)
        case BinaryResult(data=data, path=None | "-"):
            sys.stdout.buffer.write(data)
        case BinaryResult(data=data, path=str() as path):
            Path(path).write_bytes(data)
        case ExitWith(result=inner, exit_code=code):
            render(inner, output_format)
            raise typer.Exit(code)
        case _:
            raise TypeError(f"a command returned {type(result).__name__}, which has no rendering")
