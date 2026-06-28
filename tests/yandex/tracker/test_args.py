"""TDD for tracker CLI arg types — parse_fields JSON coercion."""

import pytest
import typer

from ycli.yandex.tracker._args import parse_fields


def test_parse_fields_coerces_json_with_string_fallback():
    out = parse_fields(["sprint=123", "flag=true", 'project={"id": 5}', "name=hello"])
    assert out == {"sprint": 123, "flag": True, "project": {"id": 5}, "name": "hello"}


def test_parse_fields_empty_is_empty_dict():
    assert parse_fields(None) == {}
    assert parse_fields([]) == {}


def test_parse_fields_missing_equals_raises():
    with pytest.raises(typer.BadParameter):
        parse_fields(["noequalshere"])
