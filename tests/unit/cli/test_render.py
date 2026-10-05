"""``render`` — the one place a command's return value becomes CLI output."""

import io
import sys

import pytest
import typer
from pydantic import BaseModel

from ycli.cli.output import BinaryResult, ExitWith, OutputFormat, render


class _Model(BaseModel):
    key: str


def test_none_prints_nothing(capsys):
    render(None, OutputFormat.json)
    assert capsys.readouterr().out == ""


def test_model_goes_through_the_format_strategy(capsys):
    render(_Model(key="DE-1"), OutputFormat.json)
    assert capsys.readouterr().out == '{"key":"DE-1"}\n'


@pytest.mark.parametrize(("value", "printed"), [(137, "137\n"), ("# Title\n", "# Title\n\n")])
def test_scalars_print_verbatim(capsys, value, printed):
    render(value, OutputFormat.json)
    assert capsys.readouterr().out == printed


def test_binary_result_writes_the_file(tmp_path):
    target = tmp_path / "download.bin"
    render(BinaryResult(b"\x00\x01payload", str(target)), OutputFormat.json)
    assert target.read_bytes() == b"\x00\x01payload"  # verbatim, never serialized


@pytest.mark.parametrize("path", [None, "-"])
def test_binary_result_streams_to_stdout(monkeypatch, path):
    fake_stdout = type("FakeStdout", (), {"buffer": io.BytesIO()})()
    monkeypatch.setattr(sys, "stdout", fake_stdout)
    render(BinaryResult(b"BLOB", path), OutputFormat.json)
    assert fake_stdout.buffer.getvalue() == b"BLOB"


def test_exit_with_renders_then_exits(capsys):
    with pytest.raises(typer.Exit) as caught:
        render(ExitWith(_Model(key="bad"), exit_code=3), OutputFormat.json)
    assert caught.value.exit_code == 3
    assert capsys.readouterr().out == '{"key":"bad"}\n'


def test_an_unknown_value_is_a_bug_not_silence():
    with pytest.raises(TypeError, match="returned dict"):
        render({"raw": "dict"}, OutputFormat.json)
