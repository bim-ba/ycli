"""Shared pydantic base + ref-flattening annotations for every Yandex API model.

``APIModel`` is the lenient parse base. ``KeyStr`` / ``IdStr`` / ``DisplayStr`` /
``DisplayNameStr`` normalize the API's single-field wrapper objects (``{"key": "x"}`` /
``{"id": "x"}`` / ``{"display": "x"}`` / ``{"display_name": "x"}``) down to a bare string at parse
time via ``BeforeValidator`` — so models expose plain scalars and need no per-model flattening
property. Serialization is NOT a model concern — see ``output.py``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict

if TYPE_CHECKING:
    from collections.abc import Callable


class APIModel(BaseModel):
    """Base for all Yandex API models: ignore unknown fields, allow name-or-alias population."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class Ack(APIModel):
    """Typed acknowledgement for write operations whose API response carries no body.

    MCP tools must expose an output schema (see test_every_mcp_tool_has_description_and
    _output_schema), and CLI output goes through the Serializer — a bare ``None`` return
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

        Example:
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
    def published(cls, kind: str, ident: object) -> Ack:
        """``published <kind> <ident>``.

        Example:
            >>> Ack.published("survey", "686d").detail
            'published survey 686d'
        """
        return cls(detail=f"published {kind} {ident}")

    @classmethod
    def unpublished(cls, kind: str, ident: object) -> Ack:
        """``unpublished <kind> <ident>``.

        Example:
            >>> Ack.unpublished("survey", "686d").detail
            'unpublished survey 686d'
        """
        return cls(detail=f"unpublished {kind} {ident}")

    @classmethod
    def linked(cls, kind: str, ident: object, target: object, relationship: str) -> Ack:
        """``linked <kind> <ident> -> <target> (<relationship>)``.

        Example:
            >>> Ack.linked("project", "655f", "658", "relates").detail
            'linked project 655f -> 658 (relates)'
        """
        return cls(detail=f"linked {kind} {ident} -> {target} ({relationship})")

    @classmethod
    def unlinked(cls, kind: str, ident: object, target: object) -> Ack:
        """``unlinked <kind> <ident> -> <target>``.

        Example:
            >>> Ack.unlinked("project", "655f", "658").detail
            'unlinked project 655f -> 658'
        """
        return cls(detail=f"unlinked {kind} {ident} -> {target}")

    @classmethod
    def removed(cls, item: str, value: object, *, from_: object) -> Ack:
        """``removed <item> <value!r> from <from_>``.

        Example:
            >>> Ack.removed("tag", "obsolete", from_="queue TEST").detail
            "removed tag 'obsolete' from queue TEST"
        """
        return cls(detail=f"removed {item} {value!r} from {from_}")

    @classmethod
    def cleared(cls, what: str) -> Ack:
        """``cleared <what>``.

        Example:
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
IdStr = Annotated[str | None, BeforeValidator(_extract("id"))]
DisplayStr = Annotated[str | None, BeforeValidator(_extract("display"))]
DisplayNameStr = Annotated[str | None, BeforeValidator(_extract("display_name"))]
