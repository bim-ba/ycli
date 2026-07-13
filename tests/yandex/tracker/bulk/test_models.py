"""TDD for Tracker bulk-change models — status parse, terminal predicate, typed bodies."""

from ycli.yandex.tracker.bulk.models import (
    TERMINAL_STATUSES,
    BulkChange,
    BulkIssueResult,
    BulkIssueResultList,
    BulkMove,
    BulkTransition,
    BulkUpdate,
)

STATUS_SAMPLE = {
    "id": "593cd211ef7e8a33",
    "self": "https://api.tracker.yandex.net/v3/bulkchange/593cd211ef7e8a33",
    "createdBy": {"id": "11", "display": "Full Name"},
    "createdAt": "2024-06-26T19:00:47.451+0000",
    "status": "FAILED",
    "statusText": "Изменения не выполнены",
    "executionChunkPercent": 100,
    "executionIssuePercent": 100,
    "totalIssues": 24,
    "totalCompletedIssues": 0,
}


def test_bulk_change_parses_all_fields():
    change = BulkChange.model_validate(STATUS_SAMPLE)
    assert change.id == "593cd211ef7e8a33"
    assert change.created_by == "Full Name"  # createdBy flattened to display
    assert change.status == "FAILED"
    assert change.status_text == "Изменения не выполнены"
    assert change.total_issues == 24
    assert change.total_completed_issues == 0
    assert change.self_url.endswith("/bulkchange/593cd211ef7e8a33")  # ty: ignore[unresolved-attribute]


def test_is_terminal_reflects_status():
    assert BulkChange(status="COMPLETE").is_terminal is True
    assert BulkChange(status="FAILED").is_terminal is True
    assert BulkChange(status="CREATED").is_terminal is False
    assert BulkChange(status=None).is_terminal is False
    assert {"COMPLETE", "FAILED"} == TERMINAL_STATUSES


def test_bulk_issue_result_list_flattens_issue():
    out = BulkIssueResultList.model_validate(
        [
            {
                "issue": {"key": "TEST-1", "display": "My issue"},
                "status": "FAILED",
                "statusText": "no",
                "error": {"errors": {"resolution": "bad"}, "errorMessages": []},
            }
        ]
    )
    assert isinstance(out, BulkIssueResultList)
    result = out.root[0]
    assert isinstance(result, BulkIssueResult)
    assert result.issue == "TEST-1"  # issue object flattened to key
    assert result.error is not None
    assert result.error.errors == {"resolution": "bad"}


def test_bulk_update_body_serializes():
    body = BulkUpdate(
        issues=["TEST-1", "TEST-2"], values={"type": {"name": "Task"}}, notify=True
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "issues": ["TEST-1", "TEST-2"],
        "values": {"type": {"name": "Task"}},
        "notify": True,
    }


def test_bulk_update_accepts_query_string_issues():
    body = BulkUpdate(issues="Queue: TEST", values={}).model_dump(by_alias=True, exclude_none=True)
    assert body == {"issues": "Queue: TEST", "values": {}}


def test_bulk_move_body_uses_camel_case_aliases():
    body = BulkMove(
        queue="CHECK",
        issues=["TEST-1"],
        move_all_fields=True,  # ty: ignore[unknown-argument]
        initial_status=True,  # ty: ignore[unknown-argument]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "queue": "CHECK",
        "issues": ["TEST-1"],
        "moveAllFields": True,
        "initialStatus": True,
    }


def test_bulk_transition_body_serializes():
    body = BulkTransition(
        transition="close", issues=["TEST-1"], values={"resolution": "fixed"}
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "transition": "close",
        "issues": ["TEST-1"],
        "values": {"resolution": "fixed"},
    }
