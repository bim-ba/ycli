"""Contract cases for Tracker issue ``/changelog`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent, with_query

STATUS_CHANGE = {
    "id": "ch1",
    "updatedBy": {"display": "Сава"},
    "type": "IssueUpdated",
    "fields": [
        {"field": {"id": "status"}, "from": None, "to": {"key": "done", "display": "Готово"}}
    ],
}

CASES = [
    # The default cap (500) asks for full 100-row pages and walks id=<last change id>.
    Case(
        "tracker.changelog.list",
        args=("DE-21",),
        kwargs={"limit": 500},
        cli=["tracker", "changelog", "list", "DE-21"],
        mcp=("tracker_changelog_list", {"issue_key": "DE-21"}),
        exchanges=[
            (
                Sent("GET", "issues/DE-21/changelog", {"perPage": "100"}),
                Reply(json=[STATUS_CHANGE, {"id": "ch2", "type": "IssueCommentAdded"}]),
            ),
            (
                Sent("GET", "issues/DE-21/changelog", {"perPage": "100", "id": "ch2"}),
                Reply(json=[{"id": "ch3", "type": "IssueUpdated", "fields": []}]),
            ),
            (
                Sent("GET", "issues/DE-21/changelog", {"perPage": "100", "id": "ch3"}),
                Reply(json=[]),
            ),
        ],
    ),
    Case(
        "tracker.changelog.list",
        args=("DE-22",),
        kwargs={"limit": 1},
        cli=["tracker", "changelog", "list", "DE-22", "--limit", "1"],
        mcp=("tracker_changelog_list", {"issue_key": "DE-22", "limit": 1}),
        exchanges=[
            (
                Sent("GET", "issues/DE-22/changelog", {"perPage": "1"}),
                Reply(json=[{"id": "ch9", "type": "IssueCreated"}]),
            )
        ],
    ),
    Case(
        "tracker.changelog.list",
        args=("DE-23",),
        cli=["tracker", "changelog", "list", "DE-23", "--all"],
        mcp=None,
        exchanges=[(Sent("GET", "issues/DE-23/changelog", {"perPage": "100"}), Reply(json=[]))],
    ),
]

CASES += [
    with_query(
        CASES,
        "tracker.changelog.list",
        kwargs={"field": "status", "change_type": "IssueWorkflow", "sort": "desc"},
        cli=["--field", "status", "--change-type", "IssueWorkflow", "--sort", "desc"],
        params={"field": "status", "type": "IssueWorkflow", "sort": "desc"},
    ),
]
