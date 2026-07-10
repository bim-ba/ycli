"""Pydantic models for Tracker issue checklists.

Read shapes: ``ChecklistItem`` / ``ChecklistItemList`` (the ``GET …/checklistItems`` array)
and ``Checklist`` (the issue wrapper that create/edit/delete calls return, carrying the
current ``checklistItems``). Typed write bodies: ``ChecklistItemCreate`` / ``ChecklistItemUpdate``
(with a nested ``ChecklistDeadlineInput``).
"""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class ChecklistDeadline(APIModel):
    """The ``deadline`` block on a checklist item (response shape).

    Example:
        >>> ChecklistDeadline.model_validate(
        ...     {"date": "2021-05-09T00:00:00.000+0000", "deadlineType": "date"}
        ... ).deadline_type
        'date'
    """

    date: str | None = Field(
        default=None, description="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm."
    )
    deadline_type: str | None = Field(
        default=None, alias="deadlineType", description="Deadline kind: 'date' or 'quarter'."
    )
    is_exceeded: bool | None = Field(
        default=None, alias="isExceeded", description="Whether the deadline has already passed."
    )


class ChecklistItem(APIModel):
    """A single checklist item (``GET /issues/{key}/checklistItems`` element).

    Example:
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
    deadline: ChecklistDeadline | None = Field(
        default=None, description="Per-item deadline, if set."
    )
    checklist_item_type: str | None = Field(
        default=None, alias="checklistItemType", description="Item type, e.g. 'standard'."
    )


class ChecklistItemList(RootModel[list[ChecklistItem]]):
    """A bare JSON array of checklist items (``GET …/checklistItems`` response).

    Example:
        >>> ChecklistItemList.model_validate([{"text": "step 1"}]).root[0].text
        'step 1'
    """


class Checklist(APIModel):
    """The issue wrapper returned by checklist create/edit/delete calls.

    Carries the issue ``key`` plus the current ``checklistItems`` and the done/total counts.
    ``checklist_items`` is empty when the whole checklist was cleared.

    Example:
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


class ChecklistDeadlineInput(APIModel):
    """Typed ``deadline`` block for a checklist write body.

    Example:
        >>> ChecklistDeadlineInput(date="2021-05-09T00:00:00.000+0000").model_dump(by_alias=True)
        {'date': '2021-05-09T00:00:00.000+0000', 'deadlineType': 'date'}
    """

    date: str = Field(description="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    deadline_type: str = Field(
        default="date", alias="deadlineType", description="Deadline kind: 'date' or 'quarter'."
    )


class ChecklistItemCreate(APIModel):
    """Typed request body for ``POST /issues/{key}/checklistItems`` (add an item).

    Example:
        >>> ChecklistItemCreate(text="do it").model_dump(by_alias=True, exclude_none=True)
        {'text': 'do it'}
    """

    text: str = Field(description="Item text (required).")
    checked: bool | None = Field(default=None, description="Mark the new item done.")
    assignee: str | None = Field(default=None, description="Assignee login or id for the item.")
    deadline: ChecklistDeadlineInput | None = Field(default=None, description="Item deadline.")


class ChecklistItemUpdate(APIModel):
    """Typed request body for ``PATCH /issues/{key}/checklistItems/{item_id}`` (edit an item).

    Example:
        >>> ChecklistItemUpdate(checked=True).model_dump(by_alias=True, exclude_none=True)
        {'checked': True}
    """

    text: str | None = Field(default=None, description="New item text.")
    checked: bool | None = Field(default=None, description="New done flag.")
    assignee: str | None = Field(default=None, description="New assignee login or id.")
    deadline: ChecklistDeadlineInput | None = Field(default=None, description="New item deadline.")
