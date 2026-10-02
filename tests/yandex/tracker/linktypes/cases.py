"""Contract cases for Tracker ``/linktypes`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "tracker.linktypes.list",
        cli=["tracker", "linktypes", "list"],
        mcp=("tracker_linktypes_list", {}),
        exchanges=[
            (
                Sent("GET", "linktypes"),
                Reply(json=[{"id": "relates", "inward": "Related", "outward": "Related"}]),
            )
        ],
    ),
]
