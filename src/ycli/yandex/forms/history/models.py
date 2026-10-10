"""Pydantic models for a Forms change log (``/surveys/{id}/history``)."""

from typing import Annotated

from pydantic import Field

from ycli.yandex.forms.models import UserRef
from ycli.yandex.models import APIModel
from ycli.yandex.sync.marks import Identity


class HistoryEvent(APIModel):
    """One change made to a form: who did what to which part, and when.

    Examples:
        >>> HistoryEvent.model_validate(
        ...     {"id": 7, "model": "surveyhook", "action": "POST api-v1:get_hooks_public_view"}
        ... ).model
        'surveyhook'
    """

    id: Annotated[int | None, Identity()] = Field(default=None, description="Event id (integer).")
    created: str | None = Field(default=None, description="ISO-8601 time of the change.")
    user: UserRef | None = Field(default=None, description="Who made the change.")
    model: str | None = Field(
        default=None, description="What changed, e.g. survey, surveyquestion, surveyhook."
    )
    action: str | None = Field(default=None, description="The request that made the change.")


class HistoryPage(APIModel):
    """One page of ``GET /surveys/{id}/history`` — the cursor and its events (internal).

    Examples:
        >>> HistoryPage.model_validate({"iteration_key": 5, "limit": 2, "items": []}).limit
        2
    """

    iteration_key: int | None = Field(default=None, description="Cursor of the next page.")
    limit: int | None = Field(default=None, description="Events per page.")
    items: list[HistoryEvent] = Field(default_factory=list, description="The page's events.")
