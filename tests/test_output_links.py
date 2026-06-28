"""Tracker keys become clickable links in pretty tables on a TTY, and stay bare otherwise."""

from __future__ import annotations

import io

from pydantic import BaseModel
from rich.console import Console

from ycli.output import OutputFormat, SerializationStrategy, Serializer


class _Row(BaseModel):
    key: str
    summary: str


def _render(model: BaseModel, *, terminal: bool) -> str:
    console = Console(file=io.StringIO(), force_terminal=terminal, width=200)
    Serializer.serialize(model, SerializationStrategy.from_format(OutputFormat.pretty), console)
    return console.file.getvalue()


def test_key_is_linked_on_terminal():
    out = _render(_Row(key="ABC-1", summary="x"), terminal=True)
    assert "tracker.yandex.ru/ABC-1" in out  # the OSC8 target


def test_key_is_bare_when_not_terminal():
    out = _render(_Row(key="ABC-1", summary="x"), terminal=False)
    assert "tracker.yandex.ru" not in out
    assert "ABC-1" in out
