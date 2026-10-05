"""Contract cases for Tracker ``/myself`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "tracker.me.get",
        cli=["tracker", "me", "get"],
        mcp=("tracker_me_get", {}),
        exchanges=[
            (
                Sent("GET", "myself"),
                Reply(json={"uid": 42, "login": "alice", "display": "Alice A."}),
            )
        ],
    ),
]
