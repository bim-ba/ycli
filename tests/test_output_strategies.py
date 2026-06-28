"""output.py serialization strategies."""
from io import StringIO

from pydantic import BaseModel
from rich.console import Console

from ycli.output import AutoStrategy, JsonStrategy, PrettyStrategy, YamlStrategy


class _Row(BaseModel):
    key: str
    name: str


def _console(*, terminal: bool) -> tuple[Console, StringIO]:
    buf = StringIO()
    return Console(file=buf, force_terminal=terminal, width=200), buf


def test_json_strategy_emits_pristine_json_when_piped():
    console, buf = _console(terminal=False)
    JsonStrategy().serialize(_Row(key="ABC-1", name="x"), console)
    assert buf.getvalue().strip() == '{"key":"ABC-1","name":"x"}'


def test_yaml_strategy_emits_yaml():
    console, buf = _console(terminal=False)
    YamlStrategy().serialize(_Row(key="ABC-1", name="x"), console)
    assert "key: ABC-1" in buf.getvalue()


def test_pretty_strategy_links_key_on_terminal():
    console, buf = _console(terminal=True)
    PrettyStrategy().serialize(_Row(key="ABC-1", name="x"), console)
    assert "tracker.yandex.ru/ABC-1" in buf.getvalue()


def test_auto_strategy_is_json_when_piped():
    console, buf = _console(terminal=False)
    AutoStrategy().serialize(_Row(key="ABC-1", name="x"), console)
    assert buf.getvalue().strip().startswith("{")
