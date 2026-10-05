"""Contract cases for Tracker ``/bulkchange`` reads (see tests/contract/)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "tracker.bulk.get",
        args=("4gh",),
        cli=["tracker", "bulk", "get", "4gh"],
        mcp=("tracker_bulk_get", {"bulk_id": "4gh"}),
        exchanges=[
            (
                Sent("GET", "bulkchange/4gh"),
                Reply(json={"id": "4gh", "status": "COMPLETE", "totalIssues": 2}),
            )
        ],
    ),
    Case(
        "tracker.bulk.issues_list",
        args=("5ij",),
        cli=["tracker", "bulk", "issues-list", "5ij"],
        mcp=("tracker_bulk_issues_list", {"bulk_id": "5ij"}),
        exchanges=[
            (
                Sent("GET", "bulkchange/5ij/issues"),
                Reply(json=[{"issue": {"key": "DE-9"}, "status": "FAILED"}]),
            )
        ],
    ),
]
