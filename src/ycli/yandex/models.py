"""Shared pydantic base + ref-flattening annotations for every Yandex API model.

``APIModel`` is the lenient parse base. ``KeyStr`` / ``IdStr`` / ``DisplayStr`` /
``DisplayNameStr`` normalize the API's single-field wrapper objects (``{"key": "x"}`` /
``{"id": "x"}`` / ``{"display": "x"}`` / ``{"display_name": "x"}``) down to a bare string at parse
time via ``BeforeValidator`` — so models expose plain scalars and need no per-model flattening
property. Rendering is NOT a model concern — see ``output.py``; the one thing a model says
about its output is that it keeps the API's field names.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, RootModel

from ycli.yandex.errors import YandexNotFoundError

if TYPE_CHECKING:
    from collections.abc import Callable


class APIModel(BaseModel):
    """Base for all Yandex API models: ignore unknown fields, allow name-or-alias population.

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

    model_config = ConfigDict(extra="ignore", populate_by_name=True, serialize_by_alias=True)


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

    ok: bool = True
    detail: str = ""

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


def require_found[M](result: M, *, sentinel: Callable[[M], bool], message: str) -> M:
    """Turn an all-None model into a typed ``YandexNotFoundError``.

    Several Forms/Tracker models parse leniently, so an empty 2xx body deserializes into an
    all-None model instead of failing (a real 404 is already raised by the transport); every
    MCP ``get``-style tool over such a model guards for that itself. ``sentinel`` decides what
    "empty" means for that model (e.g. ``lambda r: r.id is None``); the caller composes
    ``message`` so the wording stays specific to the resource being fetched.

    Args:
        result: The parsed model.
        sentinel: Tells whether ``result`` is empty.
        message: The error message, specific to the resource.

    Returns:
        ``result``, when it is not empty.

    Raises:
        YandexNotFoundError: ``sentinel`` says ``result`` is empty.

    Examples:
        >>> class _Result:
        ...     value = None
        >>> require_found(_Result(), sentinel=lambda r: r.value is None, message="not found")
        Traceback (most recent call last):
            ...
        ycli.yandex.errors.YandexNotFoundError: not found
        >>> _Result.value = "x"
        >>> require_found(_Result(), sentinel=lambda r: r.value is None, message="x").value
        'x'
    """
    if sentinel(result):
        raise YandexNotFoundError(message)
    return result


def _extract(field: str) -> Callable[[Any], Any]:
    """A ``BeforeValidator`` that pulls ``field`` out of an API wrapper object.

    The Yandex APIs wrap many references as ``{"<field>": "value", …}``; this returns the bare
    value and passes a scalar or ``None`` through untouched (so the field stays ``str | None``).
    """

    def pull(value: Any) -> Any:
        return value.get(field) if isinstance(value, dict) else value

    return pull


KeyStr = Annotated[str | None, BeforeValidator(_extract("key"))]
IdStr = Annotated[str | None, BeforeValidator(_extract("id"))]
DisplayStr = Annotated[str | None, BeforeValidator(_extract("display"))]
DisplayNameStr = Annotated[str | None, BeforeValidator(_extract("display_name"))]
