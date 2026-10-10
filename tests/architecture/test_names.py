"""``-o name``: the item of every listing names itself, or says why it cannot.

A reply model marks the one field the read command of its resource takes with ``Identity()``
(``docs/conventions/resources.md``); ``-o name`` prints it, so
``ycli … list -o name | xargs -n1 ycli … get`` works.
"""

from __future__ import annotations

import inspect
from typing import Annotated, Any, get_origin, get_type_hints

from tests.snapshots._surface import cli_leaves
from ycli.cli.output import _identifier, _kinds, has_names
from ycli.yandex.core.listing import Listing
from ycli.yandex.models import APIModel, ItemList, Listed
from ycli.yandex.sync.marks import Identity

#: An item with no identifier of its own, and why. Checked both ways.
NO_NAME = {
    "ycli.yandex.forms.access.models.Permission": "a grant is told by what it gives and to whom",
    "ycli.yandex.forms.models.FileOut": "a file being checked is not read back by any command",
    "ycli.yandex.tracker.entities.models.Link": "a link is told by its two ends",
    "ycli.yandex.tracker.gaps.models.UserGaps": "the absences of a user, not one object",
    "ycli.yandex.wiki.resources.models.ResourceItem": "wraps a file or a grid of another kind",
    **{
        f"ycli.yandex.datalens.schemas.{name}": (
            "a listing of several kinds: an id alone does not say which command reads it"
        )
        for name in (
            "collection.GetStructureItemsResultItemsItemVariant1",
            "collection.GetStructureItemsResultItemsItemVariant2",
            "collection.StructureItemEntry",
            "shared.OtherKind",
        )
    },
    "ycli.yandex.datalens.schemas.shared.SubjectWithBindings": (
        "who has access, told by the subject and the role together"
    ),
}


def _returns() -> dict[str, Any]:
    """What every command says it returns, by its path."""
    return {
        path: get_type_hints(inspect.unwrap(command.callback)).get("return")
        for path, command in cli_leaves().items()
    }


def _is_listing(declared: object) -> bool:
    plain = isinstance(declared, type) and issubclass(declared, ItemList | Listed)
    return get_origin(declared) is Listing or plain


def _name(kind: type) -> str:
    return f"{kind.__module__}.{kind.__qualname__}"


def unnamed(returns: dict[str, Any]) -> dict[str, list[str]]:
    """The item classes of listings that have no one ``Identity()`` field, with their commands."""
    found: dict[str, list[str]] = {}
    for path, declared in returns.items():
        if _is_listing(declared):
            for kind in _kinds(declared):
                if _identifier(kind) is None:
                    found.setdefault(_name(kind), []).append(path)
    return found


def test_the_item_of_every_listing_names_itself_or_says_why_not():
    found = unnamed(_returns())
    # Every class by its own name: none is excused by where it lives.
    unexplained = found.keys() - NO_NAME.keys()
    assert not unexplained, {name: found[name] for name in unexplained}
    assert not NO_NAME.keys() - found.keys(), "a reason for an item that names itself"


def test_the_check_bites():
    class _Marked(APIModel):
        id: int | None = None

    class _Twice(APIModel):
        id: Annotated[int, Identity()]
        key: Annotated[str, Identity()]

    found = unnamed({"x list": Listing[_Marked], "y list": ItemList[_Twice], "z get": _Marked})
    assert found == {_name(_Marked): ["x list"], _name(_Twice): ["y list"]}


def test_what_is_read_made_or_changed_is_named_where_the_listing_is():
    """A resource whose listing prints names prints the name of the object it makes too."""
    groups: dict[str, dict[str, Any]] = {}
    for path, declared in _returns().items():
        group, _, command = path.rpartition(" ")
        groups.setdefault(group, {})[command] = declared
    silent = [
        f"{group} {command}"
        for group, commands in groups.items()
        if "list" in commands and has_names(commands["list"])
        for command in ("create", "get", "update")
        if command in commands and not has_names(commands[command])
    ]
    assert not silent
