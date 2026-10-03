"""Pydantic models for Tracker link types (LinkType + LinkTypeList)."""

from __future__ import annotations

from pydantic import RootModel

from ycli.yandex.tracker.models import LinkType


class LinkTypeList(RootModel[list[LinkType]]):
    """A bare JSON array of link types.

    Examples:
        >>> LinkTypeList.model_validate([{"id": "relates"}]).root[0].id
        'relates'
    """
