"""Property accessors on the Issue model — both the populated and the None branch."""

from ycli.yandex.tracker.issues.models import Issue


def test_key_and_display_properties_populated():
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
    assert issue.type_key == "task"
    assert issue.status_key == "open"
    assert issue.priority_key == "normal"
    assert issue.epic_key == "DE-100"
    assert issue.parent_key == "DE-99"
    assert issue.queue_key == "DE"
    assert issue.assignee_display == "Сава"


def test_key_and_display_properties_none():
    issue = Issue.model_validate({"key": "DE-1"})
    assert issue.type_key is None
    assert issue.status_key is None
    assert issue.priority_key is None
    assert issue.epic_key is None
    assert issue.parent_key is None
    assert issue.queue_key is None
    assert issue.assignee_display is None
