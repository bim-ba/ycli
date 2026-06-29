"""Issue ref fields flatten to bare scalars (key/display extracted at parse time)."""

from ycli.yandex.tracker.issues.models import Issue


def test_ref_fields_flatten_to_scalars():
    issue = Issue.model_validate(
        {
            "key": "DE-1",
            "type": {"key": "task"},
            "status": {"key": "open"},
            "priority": {"key": "normal"},
            "epic": {"key": "DE-100"},
            "parent": {"key": "DE-99"},
            "queue": {"key": "DE"},
            "assignee": {"display": "Сава"},
        }
    )
    assert issue.type == "task"
    assert issue.status == "open"
    assert issue.priority == "normal"
    assert issue.epic == "DE-100"
    assert issue.parent == "DE-99"
    assert issue.queue == "DE"
    assert issue.assignee == "Сава"


def test_ref_fields_default_to_none():
    issue = Issue.model_validate({"key": "DE-1"})
    assert issue.type is None
    assert issue.status is None
    assert issue.priority is None
    assert issue.epic is None
    assert issue.parent is None
    assert issue.queue is None
    assert issue.assignee is None
