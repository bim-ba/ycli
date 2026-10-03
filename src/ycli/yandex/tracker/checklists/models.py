"""Pydantic models for Tracker issue checklists.

Read shapes: ``ChecklistItem`` / ``ChecklistItemList`` (the ``GET …/checklistItems`` array)
and ``Checklist`` (the issue wrapper that create/edit/delete calls return, carrying the
current ``checklistItems``). Typed write bodies: ``ChecklistItemCreate`` / ``ChecklistItemUpdate``
(with a nested ``DeadlineInput``).
"""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)
from ycli.yandex.tracker.models import Deadline, DeadlineInput


class ChecklistItem(APIModel):
    """A single checklist item (``GET /issues/{key}/checklistItems`` element).

    Examples:
        >>> ChecklistItem.model_validate({"id": "5f", "text": "do it", "checked": False}).text
        'do it'
    """

    id: str | None = Field(default=None, description="Checklist item id.")
    text: str | None = Field(default=None, description="Item text.")
    text_html: str | None = Field(
        default=None, alias="textHtml", description="Item text rendered to HTML."
    )
    checked: bool | None = Field(default=None, description="Whether the item is marked done.")
    assignee: DisplayStr = Field(
        default=None, description="Display name of the item assignee, if any."
    )
    deadline: Deadline | None = Field(default=None, description="Per-item deadline, if set.")
    checklist_item_type: str | None = Field(
        default=None, alias="checklistItemType", description="Item type, e.g. 'standard'."
    )


class ChecklistItemList(RootModel[list[ChecklistItem]]):
    """A bare JSON array of checklist items (``GET …/checklistItems`` response).

    Examples:
        >>> ChecklistItemList.model_validate([{"text": "step 1"}]).root[0].text
        'step 1'
    """


class Checklist(APIModel):
    """The issue wrapper returned by checklist create/edit/delete calls.

    Carries the issue ``key`` plus the current ``checklistItems`` and the done/total counts.
    ``checklist_items`` is empty when the whole checklist was cleared.

    Examples:
        >>> Checklist.model_validate(
        ...     {"key": "ORG-3", "checklistItems": [{"text": "a"}], "checklistTotal": 1}
        ... ).checklist_items[0].text
        'a'
    """

    key: str | None = Field(default=None, description="Key of the issue the checklist belongs to.")
    checklist_items: list[ChecklistItem] = Field(
        default_factory=list,
        alias="checklistItems",
        description="Current checklist items after the change (empty once cleared).",
    )
    checklist_total: int | None = Field(
        default=None, alias="checklistTotal", description="Total number of checklist items."
    )
    checklist_done: int | str | None = Field(
        default=None, alias="checklistDone", description="Number of items marked done."
    )


class ChecklistItemCreate(APIModel):
    """Typed request body for ``POST /issues/{key}/checklistItems`` (add an item).

    Examples:
        >>> ChecklistItemCreate(text="do it").model_dump(by_alias=True, exclude_none=True)
        {'text': 'do it'}
    """

    text: str = Field(description="Item text (required).")
    checked: bool | None = Field(default=None, description="Mark the new item done.")
    assignee: str | None = Field(default=None, description="Assignee login or id for the item.")
    deadline: DeadlineInput | None = Field(default=None, description="Item deadline.")


class ChecklistItemUpdate(APIModel):
    """Typed request body for ``PATCH /issues/{key}/checklistItems/{item_id}`` (edit an item).

    Examples:
        >>> ChecklistItemUpdate(checked=True).model_dump(by_alias=True, exclude_none=True)
        {'checked': True}
    """

    text: str | None = Field(default=None, description="New item text.")
    checked: bool | None = Field(default=None, description="New done flag.")
    assignee: str | None = Field(default=None, description="New assignee login or id.")
    deadline: DeadlineInput | None = Field(default=None, description="New item deadline.")
