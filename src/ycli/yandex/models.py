"""Shared pydantic base + ref-flattening annotations for every Yandex API model.

``APIModel`` is the lenient parse base. ``KeyStr`` / ``IDStr`` / ``DisplayStr`` /
``DisplayNameStr`` normalize the API's single-field wrapper objects (``{"key": "x"}`` /
``{"id": "x"}`` / ``{"display": "x"}`` / ``{"display_name": "x"}``) down to a bare string at parse
time via ``BeforeValidator`` — so models expose plain scalars and need no per-model flattening
property. Rendering is NOT a model concern — see ``output.py``; the one thing a model says
about its output is that it keeps the API's field names.
"""

from __future__ import annotations

import logging
from functools import cache
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Literal, get_args

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    RootModel,
    SecretStr,
    model_serializer,
)

#: The order of a sorted listing.
SortDirection = Literal["asc", "desc"] | str
#: Where a group is kept: the organization's directory, the cloud, Yandex ID or the staff list.
GroupSource = Literal["dir", "cloud", "com", "staff"] | str

if TYPE_CHECKING:
    from collections.abc import Callable


logger = logging.getLogger("ycli.models")

#: How the description of a request field begins when the API accepts the field and does
#: nothing with it. The field stays (docs/conventions/resources.md); setting it logs a warning.
IGNORED_BY_API = "Ignored by the API: "


def ignored_fields(model: type[BaseModel]) -> tuple[tuple[str, str], ...]:
    """The fields of ``model`` the API ignores, each with the rest of its description.

    Args:
        model: The model of a request body.

    Returns:
        A ``(field name, what happens instead)`` pair per ignored field.

    Examples:
        >>> from pydantic import Field
        >>> class Body(APIModel):
        ...     name: str | None = None
        ...     draft: bool | None = Field(default=None, description=IGNORED_BY_API + "no effect.")
        >>> ignored_fields(Body)
        (('draft', 'no effect.'),)
    """
    return tuple(
        (name, field.description.removeprefix(IGNORED_BY_API))
        for name, field in model.model_fields.items()
        if field.description and field.description.startswith(IGNORED_BY_API)
    )


def warn_ignored(name: str, why: str) -> None:
    """Log that the caller set ``name``, which the API ignores, with the reason ``why``.

    Args:
        name: The field or parameter the caller set.
        why: What happens instead, the text after ``IGNORED_BY_API`` in its description.
    """
    logger.warning("`%s` is ignored by the API: %s", name, why)


class APIModel(BaseModel):
    """Base for all Yandex API models: keep unknown fields, allow name-or-alias population.

    A reply keeps a field the model does not declare (``extra="allow"``), so what Yandex adds
    is printed at once, untyped; a request body inherits :class:`RequestBody`, which refuses it.

    ``serialize_by_alias`` keeps the API's field names (``createdAt``) in every dump, so the
    CLI and the MCP server print the same keys the vendor docs show, while Python code reads
    snake_case attributes. Tracker is camelCase on the wire; Wiki and Forms are snake_case.

    Examples:
        >>> from pydantic import Field
        >>> class Item(APIModel):
        ...     created_at: str = Field(alias="createdAt")
        >>> Item(created_at="today").model_dump()
        {'createdAt': 'today'}
    """

    # ``hide_input_in_errors``: a value that fails validation is quoted in the error's text,
    # and the value may be a body with a password in it (a union is refused by its tag
    # before any ``SecretStr`` is built). The error still names the field and what is wrong.
    model_config = ConfigDict(
        extra="allow", validate_by_name=True, serialize_by_alias=True, hide_input_in_errors=True
    )

    # No return annotation, on purpose: with one, pydantic replaces the model's serialization
    # schema with that type, and every MCP output schema loses its fields
    # (``tests/snapshots/mcp_output_schemas.txt`` would change).
    @model_serializer(mode="wrap")
    def _as_sent(self, handler, info):  # noqa: ANN001, ANN202
        """The usual dump; as a request body (``WIRE``), without the fields left unset.

        A secret (``SecretStr``) is dumped masked, as pydantic dumps it, and as its own value
        in a request body only.

        A ``None`` is an absence and is dropped, except where the caller could only have meant
        it: in a field with no default (``page`` of a redirect: ``null`` removes the redirect)
        and in a key the model does not declare (Tracker clears a field given as
        ``assignee=null``).
        """
        data = handler(self)
        if not (info.context or {}).get("wire"):
            return data
        # The one place a secret leaves its mask: the request has to carry the value itself.
        for name, key in _secret_fields(type(self)):
            if key in data:
                data[key] = _revealed(getattr(self, name))
        optional = _optional_keys(type(self))
        return {
            key: value for key, value in data.items() if value is not None or key not in optional
        }


#: The serialization context of a request body: ``body.model_dump(context=WIRE)``.
WIRE: dict[str, Any] = {"wire": True}


def _is_secret(field: Any) -> bool:
    """Whether the JSON schema ``field`` is a secret, or a map, a list or a union of secrets."""
    if not isinstance(field, dict):
        return False
    held = [*field.get("anyOf", []), field.get("additionalProperties"), field.get("items")]
    return bool(field.get("writeOnly")) or any(_is_secret(part) for part in held)


@cache
def secret_keys(model: type[BaseModel]) -> frozenset[str]:
    """The keys of a body of ``model``, at any depth, whose values are secrets.

    A secret in a request body is a ``SecretStr`` (or a map of them): pydantic masks it
    wherever the model is printed, and it goes out as it is only in a request
    (:class:`APIModel`). What prints a request before it is sent masks these keys by name.

    Args:
        model: The class of a request body.

    Returns:
        The names, as the API takes them, of the secret fields of ``model`` and of every
        model it holds.

    Examples:
        >>> class Login(RequestBody):
        ...     user: str
        ...     password: SecretStr
        ...     headers: dict[str, SecretStr] | None = None
        >>> sorted(secret_keys(Login))
        ['headers', 'password']
    """
    found: set[str] = set()
    pending: list[Any] = [model.model_json_schema()]
    while pending:
        schema = pending.pop()
        if isinstance(schema, dict):
            properties = schema.get("properties")
            if isinstance(properties, dict):
                found |= {name for name, field in properties.items() if _is_secret(field)}
            pending += schema.values()
        elif isinstance(schema, list):
            pending += schema
    return frozenset(found)


def _holds_secret(annotation: Any) -> bool:
    """Whether a field of this type is a ``SecretStr`` or holds one (``dict[str, SecretStr]``)."""
    return annotation is SecretStr or any(_holds_secret(part) for part in get_args(annotation))


@cache
def _secret_fields(model: type[BaseModel]) -> tuple[tuple[str, str], ...]:
    """The secret fields of ``model`` itself: each attribute and the key it is dumped under."""
    return tuple(
        (name, field.serialization_alias or field.alias or name)
        for name, field in model.model_fields.items()
        if _holds_secret(field.annotation)
    )


def _revealed(value: Any) -> Any:
    """``value`` with every secret in it replaced by what it hides: only for a request."""
    if isinstance(value, SecretStr):
        return value.get_secret_value()
    if isinstance(value, dict):
        return {key: _revealed(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_revealed(item) for item in value]
    return value


@cache
def _optional_keys(model: type[BaseModel]) -> frozenset[str]:
    """The keys a dump of ``model`` may hold for its fields that have a default."""
    return frozenset(
        key
        for name, field in model.model_fields.items()
        if not field.is_required()
        for key in (name, field.alias, field.serialization_alias)
        if key
    )


class RequestBody(APIModel):
    """Base for a request body: a field the model does not declare is an error, not sent.

    A reply keeps what Yandex adds (``APIModel`` is open); a body is closed, so a mistyped key
    fails where the body is built, with the field's name, instead of reaching the API.

    Examples:
        >>> class Rename(RequestBody):
        ...     name: str
        >>> Rename.model_validate({"name": "Sprint", "nmae": "x"})
        Traceback (most recent call last):
            ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for Rename
        nmae
          Extra inputs are not permitted [type=extra_forbidden]
            For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden
    """

    model_config = ConfigDict(extra="forbid")


class WarnsOnIgnored(RequestBody):
    """A request body with a field the API ignores: giving that field a value logs a warning.

    A body model that marks a field with ``IGNORED_BY_API`` inherits from this class, so that
    only such models pay for the check; ``tests/architecture/test_conventions.py`` fails on a
    marked model that does not.

    Examples:
        >>> from pydantic import Field
        >>> class Body(WarnsOnIgnored):
        ...     draft: bool | None = Field(default=None, description=IGNORED_BY_API + "no effect.")
        >>> Body.__ignored__
        (('draft', 'no effect.'),)
    """

    # The fields of the class the API ignores, found once per class.
    __ignored__: ClassVar[tuple[tuple[str, str], ...]] = ()

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        cls.__ignored__ = ignored_fields(cls)

    def model_post_init(self, context: Any, /) -> None:
        """Warn when the caller gives a value to a field the API ignores."""
        for name, why in self.__ignored__:
            if name in self.model_fields_set and getattr(self, name) is not None:
                warn_ignored(name, why)


class ItemList[T](RootModel[list[T]]):
    """A bare JSON array of items: what a listing returns, flat.

    ``ItemList[Board]`` parses ``[{...}, {...}]`` into boards, kept in ``root``.

    Examples:
        >>> class Item(APIModel):
        ...     key: str
        >>> ItemList[Item].model_validate([{"key": "a"}, {"key": "b"}]).root[1].key
        'b'
    """


class Ack(APIModel):
    """Typed acknowledgement for write operations whose API response carries no body.

    MCP tools must expose an output schema (see test_every_mcp_tool_has_description_and
    _output_schema), and the CLI renders what a command returns — a bare ``None`` return
    satisfies neither, so bodyless writes (deletes, clears, aborts) return an ``Ack``.

    The factory classmethods below are the single canonical source for every write op's
    ``detail`` text — both ``cli.py`` and ``mcp.py`` call the same factory for a given
    operation, so the two surfaces can never drift apart on wording again.
    """

    ok: bool = Field(default=True, description="Whether the write succeeded.")
    detail: str = Field(default="", description="What was done, e.g. `deleted board 5`.")

    @classmethod
    def deleted(
        cls, kind: str, ident: object, *, on: object | None = None, from_: object | None = None
    ) -> Ack:
        """``deleted <kind> <ident>`` — optionally qualified with its container.

        Pass at most one of ``on`` (an "attached to" relationship, e.g. a comment on an
        issue) or ``from_`` (a "member of" relationship, e.g. a macro from a queue).

        Args:
            kind: What was affected, e.g. ``board``.
            ident: Its id.
            on: The thing it was attached to.
            from_: The thing it was a member of.

        Returns:
            The acknowledgement.

        Examples:
            >>> Ack.deleted("board", 5).detail
            'deleted board 5'
            >>> Ack.deleted("column", 5, on="board 73").detail
            'deleted column 5 on board 73'
            >>> Ack.deleted("macro", 3, from_="queue TEST").detail
            'deleted macro 3 from queue TEST'
        """
        detail = f"deleted {kind} {ident}"
        if on is not None:
            detail += f" on {on}"
        elif from_ is not None:
            detail += f" from {from_}"
        return cls(detail=detail)

    @classmethod
    def restored(cls, kind: str, ident: object, *, in_: object) -> Ack:
        """``restored <kind> <ident> in <in_>``.

        Args:
            kind: What was affected, e.g. ``board``.
            ident: Its id.
            in_: The container it was restored in.

        Returns:
            The acknowledgement.

        Examples:
            >>> Ack.restored("answer", 7, in_="survey 686d").detail
            'restored answer 7 in survey 686d'
        """
        return cls(detail=f"restored {kind} {ident} in {in_}")

    @classmethod
    def published(cls, kind: str, ident: object) -> Ack:
        """``published <kind> <ident>``.

        Args:
            kind: What was affected, e.g. ``board``.
            ident: Its id.

        Returns:
            The acknowledgement.

        Examples:
            >>> Ack.published("survey", "686d").detail
            'published survey 686d'
        """
        return cls(detail=f"published {kind} {ident}")

    @classmethod
    def unpublished(cls, kind: str, ident: object) -> Ack:
        """``unpublished <kind> <ident>``.

        Args:
            kind: What was affected, e.g. ``board``.
            ident: Its id.

        Returns:
            The acknowledgement.

        Examples:
            >>> Ack.unpublished("survey", "686d").detail
            'unpublished survey 686d'
        """
        return cls(detail=f"unpublished {kind} {ident}")

    @classmethod
    def linked(cls, kind: str, ident: object, target: object, relationship: str) -> Ack:
        """``linked <kind> <ident> -> <target> (<relationship>)``.

        Args:
            kind: What was affected, e.g. ``board``.
            ident: Its id.
            target: What it was linked to.
            relationship: The link's relationship.

        Returns:
            The acknowledgement.

        Examples:
            >>> Ack.linked("project", "655f", "658", "relates").detail
            'linked project 655f -> 658 (relates)'
        """
        return cls(detail=f"linked {kind} {ident} -> {target} ({relationship})")

    @classmethod
    def unlinked(cls, kind: str, ident: object, target: object) -> Ack:
        """``unlinked <kind> <ident> -> <target>``.

        Args:
            kind: What was affected, e.g. ``board``.
            ident: Its id.
            target: What it was unlinked from.

        Returns:
            The acknowledgement.

        Examples:
            >>> Ack.unlinked("project", "655f", "658").detail
            'unlinked project 655f -> 658'
        """
        return cls(detail=f"unlinked {kind} {ident} -> {target}")

    @classmethod
    def removed(cls, item: str, value: object, *, from_: object) -> Ack:
        """``removed <item> <value!r> from <from_>``.

        Args:
            item: What was removed, e.g. ``tag``.
            value: The removed value.
            from_: The thing it was removed from.

        Returns:
            The acknowledgement.

        Examples:
            >>> Ack.removed("tag", "obsolete", from_="queue TEST").detail
            "removed tag 'obsolete' from queue TEST"
        """
        return cls(detail=f"removed {item} {value!r} from {from_}")

    @classmethod
    def cleared(cls, what: str) -> Ack:
        """``cleared <what>``.

        Args:
            what: What was cleared.

        Returns:
            The acknowledgement.

        Examples:
            >>> Ack.cleared("search scroll resources").detail
            'cleared search scroll resources'
        """
        return cls(detail=f"cleared {what}")


def _extract(field: str) -> Callable[[Any], Any]:
    """A ``BeforeValidator`` that pulls ``field`` out of an API wrapper object.

    The Yandex APIs wrap many references as ``{"<field>": "value", …}``; this returns the bare
    value and passes a scalar or ``None`` through untouched (so the field stays ``str | None``).
    """

    def pull(value: Any) -> Any:
        return value.get(field) if isinstance(value, dict) else value

    return pull


KeyStr = Annotated[str | None, BeforeValidator(_extract("key"))]
IDStr = Annotated[str | None, BeforeValidator(_extract("id"))]
DisplayStr = Annotated[str | None, BeforeValidator(_extract("display"))]
DisplayNameStr = Annotated[str | None, BeforeValidator(_extract("display_name"))]
