"""Pydantic models for Tracker issue transitions (Transition + TransitionList)."""
from __future__ import annotations

from pydantic import RootModel

from ycli.yandex.tracker._models import _Lenient


class Transition(_Lenient):
    """An available issue transition (``/issues/{key}/transitions`` item).

    Example:
        >>> Transition.model_validate({"id": "close", "display": "Close"}).id
        'close'
    """

    id: str | None = None
    display: str | None = None


class TransitionList(RootModel[list[Transition]]):
    """A bare JSON array of transitions.

    Example:
        >>> TransitionList.model_validate([{"id": "close"}]).root[0].id
        'close'
    """
