"""Pydantic models for Tracker link types (LinkType + LinkTypeList)."""
from __future__ import annotations

from pydantic import RootModel

from ycli.yandex.tracker._models import _Lenient


class LinkType(_Lenient):
    """A link type descriptor (``/linktypes`` item).

    Example:
        >>> LinkType.model_validate({"id": "relates", "inward": "x", "outward": "y"}).id
        'relates'
    """

    id: str | None = None
    inward: str | None = None
    outward: str | None = None


class LinkTypeList(RootModel[list[LinkType]]):
    """A bare JSON array of link types.

    Example:
        >>> LinkTypeList.model_validate([{"id": "relates"}]).root[0].id
        'relates'
    """
