"""Pydantic models for Tracker issue transitions (Transition + ItemList[Transition])."""

from typing import Annotated

from pydantic import ConfigDict, Field

from ycli.yandex.models import APIModel
from ycli.yandex.sync.marks import Identity
from ycli.yandex.tracker.models import KeyedReference, Reference


class Transition(APIModel):
    """An available issue transition (``/issues/{key}/transitions`` item).

    The GET list endpoint returns a top-level ``display`` field.
    The POST ``/_execute`` endpoint returns a ``to`` object with the target status.

    Examples:
        >>> Transition.model_validate({"id": "close", "display": "Close"}).id
        'close'
        >>> t = Transition.model_validate(
        ...     {"id": "close", "to": {"key": "closed", "display": "Closed"}}
        ... )
        >>> t.to.display
        'Closed'
    """

    id: Annotated[str | None, Identity()] = Field(
        default=None, description="Transition identifier, e.g. ``close``."
    )
    display: str | None = Field(
        default=None,
        description="Display name of the transition, as on the Tracker button.",
    )  # present on the GET list response
    to: KeyedReference | None = Field(
        default=None, description="Status the transition leads to; present on the execute response."
    )  # present on the POST _execute response (the target status)
    self_url: str | None = Field(
        default=None, alias="self", description="API resource URL of the transition."
    )
    screen: Reference | None = Field(
        default=None, description="The screen the transition shows before it runs, if any."
    )


class TransitionExecute(APIModel):
    """Typed request body for ``POST /issues/{key}/transitions/{id}/_execute``.

    Open-ended: any issue field can be set on transition (e.g. a resolution when closing), so
    ``extra="allow"`` lets arbitrary fields pass through
    unvalidated while the common fields below still document themselves in the MCP schema.

    Examples:
        >>> TransitionExecute(resolution="fixed").model_dump(exclude_none=True)
        {'resolution': 'fixed'}
    """

    model_config = ConfigDict(extra="allow")

    comment: str | None = Field(default=None, description="Comment to add with the transition.")
    resolution: str | None = Field(
        default=None, description="Resolution key to set, e.g. when closing an issue."
    )
