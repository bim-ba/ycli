"""Kinds are found by the file a resource adds, and listed by `ycli sync kinds`."""

import json
import sys
import types
from http import HTTPMethod
from typing import Any

from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.yandex import registry
from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.models import RequestBody
from ycli.yandex.sync.document import Link
from ycli.yandex.sync.formats import YAMLFile
from ycli.yandex.sync.kind import Kind


class Rename(RequestBody):
    name: str | None = None


def _declare(monkeypatch, module: str, *kinds: Kind) -> None:
    """Give one resource a `sync` module, as a file added to its package would."""
    made = types.ModuleType(module)
    for index, kind in enumerate(kinds):
        setattr(made, f"KIND_{index}", kind)
    setattr(made, "NOT_A_KIND", "a name of another sort is passed over")  # noqa: B010
    monkeypatch.setitem(sys.modules, module, made)
    found = registry.find_spec
    monkeypatch.setattr(registry, "find_spec", lambda name: made if name == module else found(name))


def _read(thing_id: int) -> Endpoint[Any]:
    return Endpoint(HTTPMethod.GET, f"things/{thing_id}")


def _kind(name: str) -> Kind:
    return Kind(name=name, layout=YAMLFile(), link=Link, content=Rename, read=_read)


def test_a_kind_is_found_by_the_sync_module_of_its_resource(monkeypatch):
    before = [kind.name for kind in registry.kinds()]
    assert before == ["tracker/trigger", "wiki/page"]  # declared by their resources, listed nowhere
    _declare(monkeypatch, "ycli.yandex.forms.surveys.sync", _kind("forms/survey"))
    _declare(monkeypatch, "ycli.yandex.tracker.components.sync", _kind("tracker/component"))
    names = [kind.name for kind in registry.kinds()]
    # A new resource is picked up by the file it adds; the order is by name.
    assert names == ["forms/survey", "tracker/component", "tracker/trigger", "wiki/page"]


def test_sync_kinds_lists_what_the_registry_holds(monkeypatch):
    _declare(monkeypatch, "ycli.yandex.forms.surveys.sync", _kind("forms/survey"))
    result = CliRunner().invoke(cli.app, ["-o", "json", "sync", "kinds"])
    assert result.exit_code == 0, result.output
    listed = {row["name"]: row for row in json.loads(result.stdout)}
    assert listed["forms/survey"] == {
        "name": "forms/survey",
        "file": ".yaml",
        "operations": ["read"],
        "version": "none: the fingerprint of the content alone",
        "about": "One file of a repository as the object it stands for: its link and its content.",
    }
    # The two first kinds, as their resources declare them.
    assert listed["tracker/trigger"]["operations"] == ["read", "find", "create", "update"]
    assert listed["tracker/trigger"]["version"].startswith("sent with the write")
    assert listed["wiki/page"]["file"] == ".md"
    assert listed["wiki/page"]["operations"] == ["read", "find", "create", "update", "delete"]
    assert listed["wiki/page"]["version"] == "read and compared before the write"
    # What a kind is comes from the first line of the docstring of the module that declares it.
    assert listed["wiki/page"]["about"] == (
        "A Wiki page as a file: wiki/<slug>.md, its text under a header."
    )
    assert listed["tracker/trigger"]["about"] == (
        "A trigger of a queue as a file: tracker/queues/<queue>/triggers/<id>.yaml."
    )
