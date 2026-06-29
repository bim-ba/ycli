"""output.py serialization strategies."""

from io import StringIO

from pydantic import BaseModel
from rich.console import Console

from ycli.cli.output import (
    AutoStrategy,
    JsonStrategy,
    OutputFormat,
    PrettyStrategy,
    SerializationStrategy,
    Serializer,
    YamlStrategy,
)


class _Row(BaseModel):
    key: str
    name: str


class _M(BaseModel):
    key: str


def _console(*, terminal: bool) -> tuple[Console, StringIO]:
    buf = StringIO()
    return Console(file=buf, force_terminal=terminal, width=200), buf


def test_json_strategy_emits_pristine_json_when_piped():
    console, buf = _console(terminal=False)
    JsonStrategy().render(_Row(key="ABC-1", name="x"), console)
    assert buf.getvalue().strip() == '{"key":"ABC-1","name":"x"}'


def test_yaml_strategy_emits_yaml():
    console, buf = _console(terminal=False)
    YamlStrategy().render(_Row(key="ABC-1", name="x"), console)
    assert "key: ABC-1" in buf.getvalue()


def test_pretty_strategy_renders_bare_key_on_terminal():
    console, buf = _console(terminal=True)
    PrettyStrategy().render(_Row(key="ABC-1", name="x"), console)
    out = buf.getvalue()
    assert "ABC-1" in out
    assert "tracker.yandex.ru" not in out


def test_pretty_strategy_renders_bare_key_when_piped():
    console, buf = _console(terminal=False)
    PrettyStrategy().render(_Row(key="ABC-1", name="x"), console)
    out = buf.getvalue()
    assert "ABC-1" in out
    assert "tracker.yandex.ru" not in out


def test_auto_strategy_is_json_when_piped():
    console, buf = _console(terminal=False)
    AutoStrategy().render(_Row(key="ABC-1", name="x"), console)
    assert buf.getvalue().strip().startswith("{")


def test_from_format_maps_each_choice():
    assert isinstance(SerializationStrategy.from_format(OutputFormat.json), JsonStrategy)
    assert isinstance(SerializationStrategy.from_format(OutputFormat.yaml), YamlStrategy)
    assert isinstance(SerializationStrategy.from_format(OutputFormat.pretty), PrettyStrategy)
    assert isinstance(SerializationStrategy.from_format(OutputFormat.auto), AutoStrategy)


def test_serializer_dispatches_to_strategy_render():
    buf = StringIO()
    console = Console(file=buf, force_terminal=False)
    Serializer.serialize(
        _M(key="DE-1"), SerializationStrategy.from_format(OutputFormat.json), console
    )
    assert '"key":"DE-1"' in buf.getvalue().replace(" ", "")


def test_pretty_strategy_renders_list_of_dicts():
    class _RowList(BaseModel):
        rows: list[_Row]

    console, buf = _console(terminal=True)
    PrettyStrategy().render(_RowList(rows=[_Row(key="A", name="foo")]), console)
    out = buf.getvalue()
    assert "A" in out


def test_pretty_strategy_renders_scalar_list_as_join():
    console, buf = _console(terminal=True)

    class _Tags(BaseModel):
        tags: list[str]

    PrettyStrategy().render(_Tags(tags=["alpha", "beta"]), console)
    assert "alpha, beta" in buf.getvalue()
