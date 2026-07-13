"""Issue ref fields flatten to bare scalars (key/display extracted at parse time)."""

from ycli.yandex.tracker.issues.models import Issue, IssueCreate, IssueUpdate


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


def test_issue_create_tags_operator_form_round_trips():
    """The documented {'add'|'set'|'remove': [...]} operator-edit form on tags must validate
    and dump byte-identical to what the old ``body: dict`` would have passed through."""
    raw = {"queue": "DE", "summary": "New", "tags": {"add": ["urgent"]}}
    dumped = IssueCreate.model_validate(raw).model_dump(exclude_none=True)
    assert dumped == raw

    # the plain replace-list form must still work too.
    raw_plain = {"queue": "DE", "summary": "New", "tags": ["a", "b"]}
    dumped_plain = IssueCreate.model_validate(raw_plain).model_dump(exclude_none=True)
    assert dumped_plain == raw_plain


def test_issue_update_tags_operator_form_round_trips():
    raw = {"tags": {"remove": ["stale"]}}
    dumped = IssueUpdate.model_validate(raw).model_dump(exclude_none=True)
    assert dumped == raw
