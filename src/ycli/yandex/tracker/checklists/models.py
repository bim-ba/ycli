"""Pydantic models for Tracker issue checklists.

A checklist item is ``ChecklistItem``; adding, editing or deleting one returns the issue
itself (``ycli.yandex.tracker.models.Issue``, with its ``checklistItems``). Typed write
bodies: ``ChecklistItemCreate`` / ``ChecklistItemUpdate`` (with a nested ``DeadlineInput``).
"""

from pydantic import Field

from ycli.yandex.models import (
    RequestBody,  # pydantic resolves field types via get_type_hints() at runtime
)
from ycli.yandex.tracker.models import DeadlineInput, IssueChecklistItem

#: An item of an issue's checklist. The class lives beside ``Issue``, which carries the items,
#: under a name that tells it from the item of an entity's checklist.
ChecklistItem = IssueChecklistItem


class ChecklistItemCreate(RequestBody):
    """Typed request body for ``POST /issues/{key}/checklistItems`` (add an item).

    Examples:
        >>> ChecklistItemCreate(text="do it").model_dump(exclude_none=True)
        {'text': 'do it'}
    """

    text: str = Field(description="Item text (required).")
    checked: bool | None = Field(default=None, description="Mark the new item done.")
    assignee: str | None = Field(default=None, description="Assignee login or id for the item.")
    deadline: DeadlineInput | None = Field(default=None, description="Item deadline.")


class ChecklistItemUpdate(RequestBody):
    """Typed request body for ``PATCH /issues/{key}/checklistItems/{item_id}`` (edit an item).

    Examples:
        >>> ChecklistItemUpdate(checked=True).model_dump(exclude_none=True)
        {'checked': True}
    """

    text: str | None = Field(default=None, description="New item text.")
    checked: bool | None = Field(default=None, description="New done flag.")
    assignee: str | None = Field(default=None, description="New assignee login or id.")
    deadline: DeadlineInput | None = Field(default=None, description="New item deadline.")
