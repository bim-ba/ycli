"""Contract cases for Tracker ``/bulkchange`` (see tests/contract.py).

The CLI cases pass ``--no-wait``: the ``--wait`` poll is a CLI-only flow, tested in test_cli.py.
"""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "tracker.bulk.update",
        args=(
            {
                "issues": ["DE-1", "DE-2"],
                "values": {"priority": "minor", "sprint": 5},
                "notify": True,
            },
        ),
        cli=[
            "tracker",
            "bulk",
            "update",
            "--issue",
            "DE-1",
            "--issue",
            "DE-2",
            "-F",
            "priority=minor",
            "-F",
            "sprint=5",
            "--notify",
            "--no-wait",
        ],
        mcp=(
            "tracker_bulk_update",
            {
                "body": {
                    "issues": ["DE-1", "DE-2"],
                    "values": {"priority": "minor", "sprint": 5},
                    "notify": True,
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "bulkchange/_update",
                    json={
                        "issues": ["DE-1", "DE-2"],
                        "values": {"priority": "minor", "sprint": 5},
                        "notify": True,
                    },
                ),
                Reply(json={"id": "1ab", "status": "CREATED"}, status=201),
            )
        ],
    ),
    # --query selects the issues instead of keys; with no -F the values stay an empty object.
    Case(
        "tracker.bulk.update",
        args=({"issues": "Queue: TEST", "values": {}},),
        cli=["tracker", "bulk", "update", "--query", "Queue: TEST", "--no-wait"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "bulkchange/_update", json={"issues": "Queue: TEST", "values": {}}),
                Reply(json={"id": "1ac", "status": "CREATED"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.bulk.move",
        args=(
            {
                "queue": "CHECK",
                "issues": ["DE-3"],
                "values": {"tags": ["moved"]},
                "moveAllFields": True,
                "initialStatus": True,
                "notify": True,
            },
        ),
        cli=[
            "tracker",
            "bulk",
            "move",
            "CHECK",
            "--issue",
            "DE-3",
            "-F",
            'tags=["moved"]',
            "--move-all-fields",
            "--initial-status",
            "--notify",
            "--no-wait",
        ],
        mcp=(
            "tracker_bulk_move",
            {
                "body": {
                    "queue": "CHECK",
                    "issues": ["DE-3"],
                    "values": {"tags": ["moved"]},
                    "moveAllFields": True,
                    "initialStatus": True,
                    "notify": True,
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "bulkchange/_move",
                    json={
                        "queue": "CHECK",
                        "issues": ["DE-3"],
                        "values": {"tags": ["moved"]},
                        "moveAllFields": True,
                        "initialStatus": True,
                        "notify": True,
                    },
                ),
                Reply(json={"id": "2cd", "status": "CREATED"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.bulk.move",
        args=({"queue": "ARCHIVE", "issues": "Queue: OLD"},),
        cli=["tracker", "bulk", "move", "ARCHIVE", "--query", "Queue: OLD", "--no-wait"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "bulkchange/_move", json={"queue": "ARCHIVE", "issues": "Queue: OLD"}),
                Reply(json={"id": "2ce", "status": "CREATED"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.bulk.transition",
        args=(
            {
                "transition": "close",
                "issues": ["DE-4"],
                "values": {"resolution": "fixed"},
                "notify": True,
            },
        ),
        cli=[
            "tracker",
            "bulk",
            "transition",
            "close",
            "--issue",
            "DE-4",
            "-F",
            "resolution=fixed",
            "--notify",
            "--no-wait",
        ],
        mcp=(
            "tracker_bulk_transition",
            {
                "body": {
                    "transition": "close",
                    "issues": ["DE-4"],
                    "values": {"resolution": "fixed"},
                    "notify": True,
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "bulkchange/_transition",
                    json={
                        "transition": "close",
                        "issues": ["DE-4"],
                        "values": {"resolution": "fixed"},
                        "notify": True,
                    },
                ),
                Reply(json={"id": "3ef", "status": "CREATED"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.bulk.transition",
        args=({"transition": "reopen", "issues": "Queue: QA"},),
        cli=["tracker", "bulk", "transition", "reopen", "--query", "Queue: QA", "--no-wait"],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "bulkchange/_transition",
                    json={"transition": "reopen", "issues": "Queue: QA"},
                ),
                Reply(json={"id": "3eg", "status": "CREATED"}, status=201),
            )
        ],
    ),
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
        "tracker.bulk.issues",
        args=("5ij",),
        cli=["tracker", "bulk", "issues", "5ij"],
        mcp=("tracker_bulk_issues_list", {"bulk_id": "5ij"}),
        exchanges=[
            (
                Sent("GET", "bulkchange/5ij/issues"),
                Reply(json=[{"issue": {"key": "DE-9"}, "status": "FAILED"}]),
            )
        ],
    ),
]
