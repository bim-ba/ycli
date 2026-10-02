"""The shared ``--field key=value`` parser — JSON coercion with a string fallback."""

import io

import pytest
import typer

from ycli.cli.fields import parse_fields


def test_parse_fields_coerces_json_with_string_fallback():
    out = parse_fields(["sprint=123", "flag=true", 'project={"id": 5}', "name=hello"])
    assert out == {"sprint": 123, "flag": True, "project": {"id": 5}, "name": "hello"}


def test_parse_fields_empty_is_empty_dict():
    assert parse_fields(None) == {}
    assert parse_fields([]) == {}


def test_parse_fields_missing_equals_raises():
    with pytest.raises(typer.BadParameter):
        parse_fields(["noequalshere"])


def test_structured_fields_nest_append_and_type_what_they_hold():
    out = parse_fields(
        ["a[b][c]=1", "a[b][d]=x", "t[]=true", "t[]=y", "n=null"],
        raw=["id=7", "t[]=first"],
        structured=True,
    )
    assert out == {"id": "7", "t": ["first", True, "y"], "a": {"b": {"c": 1, "d": "x"}}, "n": None}


def test_structured_fields_read_a_file_as_text(tmp_path):
    note = tmp_path / "note.txt"
    note.write_text("42")
    assert parse_fields([f"x=@{note}"], structured=True) == {"x": "42"}


def test_structured_fields_read_stdin_as_text(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("piped"))
    assert parse_fields(["x=@-"], structured=True) == {"x": "piped"}


def test_a_plain_field_keeps_an_at_sign_and_a_bracket_literal():
    assert parse_fields(["text=@alice", "a[b]=1"]) == {"text": "@alice", "a[b]": 1}


@pytest.mark.parametrize("item", ["a", "a[b=1", "a[][b]=1", "=1", "a[b]c=1"])
def test_structured_fields_reject_a_malformed_key(item):
    with pytest.raises(typer.BadParameter):
        parse_fields([item], structured=True)


@pytest.mark.parametrize("items", [["a=1", "a[b]=2"], ["a[b]=1", "a=2"], ["a=1", "a[]=2"]])
def test_structured_fields_reject_a_clash(items):
    with pytest.raises(typer.BadParameter, match="clashes"):
        parse_fields(items, structured=True)


def test_structured_fields_reject_a_missing_file(tmp_path):
    with pytest.raises(typer.BadParameter, match="cannot read"):
        parse_fields([f"x=@{tmp_path / 'nope'}"], structured=True)
