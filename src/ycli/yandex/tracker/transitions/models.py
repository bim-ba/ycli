"""Pydantic models for Tracker issue transitions (Transition + TransitionList)."""

from __future__ import annotations

from pydantic import RootModel

from ycli.yandex.models import APIModel


class StatusRef(APIModel):
    """The target status of a transition (the ``to`` object): its key + display name.

    Example:
        >>> StatusRef.model_validate({"key": "closed", "display": "Closed"}).key
        'closed'
    """

    key: str | None = None
    display: str | None = None


class Transition(APIModel):
    """An available issue transition (``/issues/{key}/transitions`` item).

    The GET list endpoint returns a top-level ``display`` field.
    The POST ``/_execute`` endpoint returns a ``to`` object with the target status.

    Example:
        >>> Transition.model_validate({"id": "close", "display": "Close"}).id
        'close'
        >>> t = Transition.model_validate(
        ...     {"id": "close", "to": {"key": "closed", "display": "Closed"}}
        ... )
        >>> t.to.display
        'Closed'
    """

    id: str | None = None
    display: str | None = None  # present on the GET list response
    to: StatusRef | None = None  # present on the POST _execute response (the target status)


class TransitionList(RootModel[list[Transition]]):
    """A bare JSON array of transitions.

    Example:
        >>> TransitionList.model_validate([{"id": "close"}]).root[0].id
        'close'
    """
