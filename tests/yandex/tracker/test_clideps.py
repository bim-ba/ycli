"""TDD for the tracker CLI deps — lazy client build + --field JSON coercion."""
import click
import pytest
import typer

from ycli.yandex.tracker._clideps import parse_fields, tracker_client
from ycli.yandex.tracker.client import TrackerClient


def test_parse_fields_coerces_json_with_string_fallback():
    out = parse_fields(["sprint=123", "flag=true", 'project={"id": 5}', "name=hello"])
    assert out == {"sprint": 123, "flag": True, "project": {"id": 5}, "name": "hello"}


def test_parse_fields_empty_is_empty_dict():
    assert parse_fields(None) == {}
    assert parse_fields([]) == {}


def test_parse_fields_missing_equals_raises():
    with pytest.raises(typer.BadParameter):
        parse_fields(["noequalshere"])


def test_tracker_client_lazy_caches_on_ctx(monkeypatch):
    built = []

    def _fake_from_env(cls):
        built.append(1)
        return "CLIENT"

    monkeypatch.setattr(TrackerClient, "from_env", classmethod(_fake_from_env))
    ctx = click.Context(click.Command("x"))  # typer.Context subclasses this; ctx.obj is all we touch
    ctx.obj = None
    assert tracker_client(ctx) == "CLIENT"
    assert tracker_client(ctx) == "CLIENT"  # cached — not rebuilt
    assert len(built) == 1
