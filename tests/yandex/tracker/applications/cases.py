"""Contract cases for Tracker ``/applications`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "tracker.applications.list",
        cli=["tracker", "applications", "list"],
        mcp=("tracker_applications_list", {}),
        exchanges=[
            (
                Sent("GET", "applications"),
                Reply(json=[{"id": "my-application", "name": "My application"}]),
            )
        ],
    ),
]
