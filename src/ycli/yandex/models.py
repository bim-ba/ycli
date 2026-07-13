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
    """

    ok: bool = True
    detail: str = ""


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
