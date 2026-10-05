"""Take everything personal out of an API reply before it becomes a fixture in a public repository.

Deny by default: a value reaches the file only when it is on a list of what is allowed, so a
name, an issue text or a file name cannot slip through for not looking like one. A reply keeps
its shape — keys, types, nesting — and that shape is what a fixture is compared by.

What stays, by the position of the value in the model of the reply:

- a key the model of that position reads, and a key that is public already (a field of
  another model of ycli, a name the service publishes);
- a string that the model lists as a ``Literal`` or an enum value at that position;
- a boolean, ``null``, and a small number under a key that does not name an identifier.

Everything else is replaced: a string by ``<key>``, a date by one constant, an identifier or a
large number by 1, 2, 3…, a key of a map (``dict[str, X]``: its keys are data) by ``<key-N>``,
any other key nothing public knows by ``<unknown-N>``. That such a key is there is the sign
that the API grew a field; its name goes only to whoever records, in :attr:`Scrubbed.unknown_keys`.
A list keeps one item per distinct shape.
"""

from __future__ import annotations

import datetime
import enum
import json
import re
import types
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, TypeAliasType, Union, get_args, get_origin

from pydantic import AliasChoices, BaseModel, RootModel

DATE_TIME = "2000-01-01T00:00:00.000+0000"
DATE = "2000-01-01"
SMALL_NUMBER = 100_000
_IDENTIFIER_KEY = re.compile(r"(?i)(^|[a-z_])u?ids?$|^version$|^self$")
_SEQUENCES = (list, tuple, set, frozenset)


@dataclass
class Scrubbed:
    """What one reply became, and what whoever records should look at."""

    body: Any = None
    # The paths, with their real names, of the keys the model of their position does not know:
    # for the eyes of whoever records, never for a file in the repository.
    unknown_keys: list[str] = field(default_factory=list)
    _numbers: int = 0

    def next_number(self) -> int:
        self._numbers += 1
        return self._numbers


def scrub(body: Any, annotation: Any = Any, public: frozenset[str] = frozenset()) -> Scrubbed:
    """``body`` with nothing personal left, read as ``annotation`` (the type of the reply).

    ``public`` is every key that is public already: a field name of some model of ycli, or a
    name the service publishes. A key the model of its position does not know is kept under
    its name only when it is one of them, and becomes ``<unknown-N>`` otherwise.

    Examples:
        >>> class Status(BaseModel):
        ...     key: Literal["open", "closed"] | str
        ...     display: str
        >>> scrub(
        ...     {"key": "open", "display": "Открыт", "votes": 3}, Status, frozenset({"votes"})
        ... ).body
        {'key': 'open', 'display': '<display>', 'votes': 3}
        >>> scrub({"key": "mine", "ivansField": 77123456}, Status).body
        {'key': '<key>', '<unknown-1>': 1}
    """
    result = Scrubbed()
    result.body = _scrub(body, annotation, "reply", "", result, public)
    return result


def _members(annotation: Any) -> list[Any]:
    """The plain types ``annotation`` allows: unions, ``Annotated`` and aliases opened up."""
    if isinstance(annotation, TypeAliasType):
        return _members(annotation.__value__)
    origin = get_origin(annotation)
    if origin is Annotated:
        return _members(get_args(annotation)[0])
    if origin in (Union, types.UnionType):
        return [member for part in get_args(annotation) for member in _members(part)]
    if isinstance(annotation, type) and issubclass(annotation, RootModel):
        return _members(annotation.model_fields["root"].annotation)
    return [annotation]


def _models(members: list[Any]) -> list[type[BaseModel]]:
    return [
        member for member in members if isinstance(member, type) and issubclass(member, BaseModel)
    ]


def _fields(model: type[BaseModel]) -> dict[str, Any]:
    """Every key ``model`` reads a field from -> the annotation of that field."""
    known: dict[str, Any] = {}
    for name, info in model.model_fields.items():
        aliases = [name, info.alias, info.serialization_alias]
        choices = info.validation_alias
        aliases += choices.choices if isinstance(choices, AliasChoices) else [choices]
        for alias in aliases:
            if isinstance(alias, str):
                known[alias] = info.annotation
    return known


def _allowed_strings(members: list[Any]) -> set[str]:
    allowed: set[str] = set()
    for member in members:
        if get_origin(member) is Literal:
            allowed.update(value for value in get_args(member) if isinstance(value, str))
        elif isinstance(member, type) and issubclass(member, enum.Enum):
            allowed.update(item.value for item in member if isinstance(item.value, str))
    return allowed


def _item_annotation(members: list[Any]) -> Any:
    for member in members:
        if get_origin(member) in _SEQUENCES and get_args(member):
            return get_args(member)[0]
    return Any


def _shape(value: Any) -> str:
    """The keys and types of ``value`` without its values: what two list items are compared by."""
    if isinstance(value, dict):
        return "{" + ",".join(f"{key}:{_shape(item)}" for key, item in sorted(value.items())) + "}"
    if isinstance(value, list):
        return "[" + ",".join(sorted({_shape(item) for item in value})) + "]"
    return type(value).__name__


def _scrub(
    value: Any, annotation: Any, key: str, path: str, result: Scrubbed, public: frozenset[str]
) -> Any:
    members = _members(annotation)
    if isinstance(value, dict):
        return _scrub_object(value, members, path, result, public)
    if isinstance(value, list):
        item = _item_annotation(members)
        kept: dict[str, Any] = {}
        for entry in value:
            scrubbed = _scrub(entry, item, key, f"{path}[]", result, public)
            kept.setdefault(_shape(scrubbed), scrubbed)
        return list(kept.values())
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int | float):
        literal = any(
            get_origin(member) is Literal and value in get_args(member) for member in members
        )
        if literal or (not _IDENTIFIER_KEY.search(key) and abs(value) < SMALL_NUMBER):
            return value
        return result.next_number() if isinstance(value, int) else float(result.next_number())
    if value in _allowed_strings(members):
        return value
    if datetime.datetime in members:
        return DATE_TIME
    if datetime.date in members:
        return DATE
    return f"<{key}>"


def _scrub_object(
    value: dict[str, Any], members: list[Any], path: str, result: Scrubbed, public: frozenset[str]
) -> dict[str, Any]:
    models = _models(members)
    mapping = next((member for member in members if get_origin(member) is dict), None)
    if mapping is not None and not models:
        # A map: its keys are data, whatever they look like.
        item = get_args(mapping)[1] if get_args(mapping) else Any
        return {
            f"<key-{number}>": _scrub(
                entry, item, f"key-{number}", f"{path}.<key-{number}>", result, public
            )
            for number, entry in enumerate(value.values(), start=1)
        }
    # A union of models: the one that knows the most of these keys reads the object. With no
    # model at all, no key is known.
    known = [_fields(model) for model in models] or [{}]
    fields = max(known, key=lambda names: len(names.keys() & value.keys()))
    scrubbed: dict[str, Any] = {}
    unknown = 0
    for name, entry in value.items():
        kept = name
        if name not in fields:
            if models:
                result.unknown_keys.append(f"{path}.{name}".lstrip("."))
            if name not in public:
                # Not a name anything public knows: only that the key is there reaches the file.
                unknown += 1
                kept = f"<unknown-{unknown}>"
        key = name if kept == name else kept.strip("<>")
        scrubbed[kept] = _scrub(entry, fields.get(name, Any), key, f"{path}.{kept}", result, public)
    return scrubbed


def strings(value: Any) -> set[str]:
    """Every string in ``value``, keys included: what a probe for a leak looks through."""
    if isinstance(value, dict):
        return {str(key) for key in value} | {
            text for item in value.values() for text in strings(item)
        }
    if isinstance(value, list):
        return {text for item in value for text in strings(item)}
    return {value} if isinstance(value, str) else set()


def dumped(document: Any) -> str:
    """A fixture file's text: stable, readable, one trailing newline."""
    return json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
