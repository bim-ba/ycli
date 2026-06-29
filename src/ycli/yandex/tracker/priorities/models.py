"""Pydantic models for Tracker priorities (Priority + PriorityList)."""

from __future__ import annotations

from pydantic import RootModel

from ycli.yandex.models import APIModel


class Priority(APIModel):
    """A priority reference (``/priorities`` item).

    Example:
        >>> Priority.model_validate({"key": "normal", "display": "Normal"}).key
        'normal'
    """

    key: str | None = None
    display: str | None = None


class PriorityList(RootModel[list[Priority]]):
    """A bare JSON array of priorities.

    Example:
        >>> PriorityList.model_validate([{"key": "normal"}]).root[0].key
        'normal'
    """
