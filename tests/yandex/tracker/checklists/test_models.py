"""Model parsing/serialization for checklists — response flattening + typed write bodies."""

from ycli.yandex.tracker.checklists.models import (
    Checklist,
    ChecklistDeadlineInput,
    ChecklistItem,
    ChecklistItemCreate,
    ChecklistItemUpdate,
)


def test_item_flattens_assignee_and_parses_deadline():
    item = ChecklistItem.model_validate(
        {
            "id": "5f",
            "text": "do it",
            "textHtml": "<b>do it</b>",
            "checked": True,
            "assignee": {"display": "Сава", "login": "sava"},
            "deadline": {"date": "2021-05-09T00:00:00.000+0000", "isExceeded": False},
            "checklistItemType": "standard",
        }
    )
    assert item.assignee == "Сава"  # DisplayStr flattens the object
    assert item.text_html == "<b>do it</b>"
    assert item.checklist_item_type == "standard"
    assert item.deadline is not None and item.deadline.is_exceeded is False


def test_checklist_wrapper_defaults_items_to_empty():
    wrapper = Checklist.model_validate({"key": "ORG-3", "checklistDone": "0"})
    assert wrapper.key == "ORG-3"
    assert wrapper.checklist_items == []
    assert wrapper.checklist_done == "0"


def test_create_body_serializes_with_aliases():
    body = ChecklistItemCreate(
        text="step 1",
        checked=True,
        assignee="sava",
        deadline=ChecklistDeadlineInput(date="2021-05-09T00:00:00.000+0000"),
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "text": "step 1",
        "checked": True,
        "assignee": "sava",
        "deadline": {"date": "2021-05-09T00:00:00.000+0000", "deadlineType": "date"},
    }


def test_update_body_drops_unset_fields():
    assert ChecklistItemUpdate(checked=False).model_dump(by_alias=True, exclude_none=True) == {
        "checked": False
    }
