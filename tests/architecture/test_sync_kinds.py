"""Every kind a resource declares holds to the rules of the file engine (`ycli sync`).

One test over the registry, so a new kind is checked by being declared: its operations are
operations of a registered service with a contract case, their marks are readable, its content
carries no secret, and the module that declares it says in one line what it is.
"""

import sys
from dataclasses import replace
from functools import partial
from http import HTTPMethod
from importlib.util import find_spec
from types import ModuleType
from typing import Annotated, Any, get_type_hints

import pytest
from pydantic import SecretStr

from tests.architecture.scanners import DOMAINS
from tests.contract import load_cases
from ycli.yandex import tracker
from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.models import RequestBody, secret_keys
from ycli.yandex.registry import kinds
from ycli.yandex.sync.document import Link
from ycli.yandex.sync.formats import YAMLFile
from ycli.yandex.sync.kind import (
    Container,
    Identity,
    Kind,
    Version,
    arguments_of,
    summary_of,
)
from ycli.yandex.tracker import queues
from ycli.yandex.wiki import pages

PACKAGE = "ycli.yandex."


def _operations(kind: Kind[Any, Any]) -> dict[str, Any]:
    newest = getattr(kind.version, "newest", None)
    return kind.operations() | ({"newest version": newest} if newest else {})


def _containers(operation: Any) -> list[str]:
    """The packages the `Container` marks of ``operation`` name."""
    hints = get_type_hints(operation, include_extras=True).values()
    marks = [mark for hint in hints for mark in getattr(hint, "__metadata__", ())]
    return [mark.of.__name__ for mark in marks if isinstance(mark, Container)]


def _problems(kind: Kind[Any, Any], recorded: set[str]) -> list[str]:
    """What is wrong with the declaration of ``kind``; ``recorded``: the operations with a case."""
    found = []
    service = kind.name.partition("/")[0]
    if service not in DOMAINS:
        found.append(f"the name does not start with a registered service: {kind.name}")
    for role, given in _operations(kind).items():
        operation = given.func if isinstance(given, partial) else given
        home = operation.__module__.removeprefix(PACKAGE).removesuffix(".endpoints")
        # `list_` in endpoints.py is the operation `list`.
        name = f"{home}.{operation.__name__.rstrip('_')}"
        if not operation.__module__.startswith(f"{PACKAGE}{service}."):
            found.append(f"{role}: {name} is not an operation of {service}")
        elif name not in recorded:
            found.append(f"{role}: {name} has no contract case")
        try:
            undecided = arguments_of(given).undecided
        except (NameError, TypeError) as error:
            found.append(f"{role}: the marks of {name} cannot be read ({error})")
            continue
        if undecided:
            found.append(f"{role}: {name} has an argument nobody decides: {list(undecided)}")
        for held in _containers(operation):
            if not held.startswith(f"{PACKAGE}{service}.") or find_spec(f"{held}.client") is None:
                found.append(f"{role}: the container of {name} is no resource of {service}: {held}")
    if secrets := secret_keys(kind.content):
        found.append(f"the content carries a secret, which a file would hold: {sorted(secrets)}")
    about = summary_of(kind).about
    if not about:
        found.append("the module that declares the kind has no docstring to say what it is")
    if "`" in about or "*" in about:
        found.append(f"what the listing says of the kind is not plain text: {about}")
    return found


def test_every_declared_kind_holds_to_the_rules():
    declared = kinds()
    assert len({kind.name for kind in declared}) == len(declared), "two kinds share a name"
    recorded = {case.operation for case in load_cases()}
    assert {kind.name: found for kind in declared if (found := _problems(kind, recorded))} == {}


class _Rename(RequestBody):
    name: str | None = None


class _Undescribed(Link):
    pass


# As a link declared in a module that says nothing of its kind.
_SILENT = ModuleType("a_module_with_no_docstring")
sys.modules[_SILENT.__name__] = _SILENT
_Undescribed.__module__ = _SILENT.__name__


class _Marked(Link):
    pass


# As a link declared in a module whose first line carries marks of its own.
_MARKED = ModuleType("a_module_with_marks", "A `thing` as a file.")
sys.modules[_MARKED.__name__] = _MARKED
_Marked.__module__ = _MARKED.__name__


class _Connection(RequestBody):
    host: str | None = None
    password: SecretStr | None = None


_REQUEST: Endpoint[Any] = Endpoint(HTTPMethod.GET, "anything")


def _get(trigger_id: Annotated[int, Identity()]) -> Endpoint[Any]:
    return _REQUEST


def _two(a: Annotated[int, Version()], b: Annotated[int, Version()]) -> Endpoint[Any]:
    return _REQUEST


def _in_a_queue(queue_id: Annotated[str, Container(queues)]) -> Endpoint[Any]:
    return _REQUEST


def _in_a_page(slug: Annotated[str, Container(pages)]) -> Endpoint[Any]:
    return _REQUEST


def _in_a_service(name: Annotated[str, Container(tracker)]) -> Endpoint[Any]:
    return _REQUEST


def _unreadable(trigger_id: int) -> Endpoint[Any]:
    return _REQUEST


def _needs_a_value(trigger_id: Annotated[int, Identity()], *, expand: str) -> Endpoint[Any]:
    return _REQUEST


for _made in (_get, _two, _unreadable, _in_a_queue, _in_a_page, _in_a_service, _needs_a_value):
    _made.__module__ = "ycli.yandex.tracker.triggers.endpoints"
for _made in (_get, _in_a_queue, _in_a_page, _in_a_service, _needs_a_value):
    _made.__name__ = "get"
# As a client whose models are imported for the type checker only: the name is not there.
_unreadable.__annotations__ = {"trigger_id": "Annotated[int, NoSuchName()]"}


_TRIGGER = Kind(name="tracker/trigger", layout=YAMLFile(), link=Link, content=_Rename, read=_get)


def _kind(**changed: Any) -> Kind[Any, Any]:
    return replace(_TRIGGER, **changed)


@pytest.mark.parametrize(
    ("kind", "said"),
    [
        (_kind(), None),
        (_kind(read=partial(_get)), None),
        (_kind(name="nowhere/thing"), "does not start with a registered service"),
        (_kind(name="wiki/page"), "is not an operation of wiki"),
        (_kind(update=_two), "tracker.triggers._two has no contract case"),
        (_kind(update=_two), "the marks of tracker.triggers._two cannot be read"),
        (_kind(delete=_unreadable), "cannot be read"),
        (_kind(content=_Connection), "carries a secret, which a file would hold: ['password']"),
        (_kind(link=_Undescribed), "has no docstring to say what it is"),
        (_kind(link=_Marked), "is not plain text: A `thing` as a file."),
        # A container is a resource of the kind's own service, named by its package.
        (_kind(read=_in_a_queue), None),
        # An argument that must have a value and that nobody names: the kind cannot be called.
        (_kind(read=_needs_a_value), "has an argument nobody decides: ['expand']"),
        (_kind(read=partial(_needs_a_value, expand="all")), None),
        (_kind(read=_in_a_page), "the container of tracker.triggers.get is no resource of tracker"),
        (_kind(read=_in_a_service), "is no resource of tracker: ycli.yandex.tracker"),
    ],
)
def test_the_check_of_a_kind_bites(kind, said):
    found = _problems(kind, recorded={"tracker.triggers.get"})
    assert found == [] if said is None else any(said in problem for problem in found), found
