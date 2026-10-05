"""Contract cases for the bulk writes of Tracker ``/bulkchange`` (see tests/contract/).

The CLI cases pass ``--no-wait``: the ``--wait`` poll is a CLI-only flow, tested in test_cli.py.
"""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.bulk.models import BulkMove, BulkTransition, BulkUpdate

BULK_CASES = [
    Case(
        "tracker.issues.update_bulk",
        args=(
            BulkUpdate.model_validate(
                {
                    "issues": ["DE-1", "DE-2"],
                    "values": {"priority": "minor", "sprint": 5},
                    "notify": True,
                }
            ),
        ),
        kwargs={"notify": True},
        cli=[
            "tracker",
            "issues",
            "update-bulk",
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
            "tracker_issues_update_bulk",
            {
                "body": {
                    "issues": ["DE-1", "DE-2"],
                    "values": {"priority": "minor", "sprint": 5},
                    "notify": True,
                },
                "notify": True,
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "bulkchange/_update",
                    {"notify": "true"},
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
        "tracker.issues.update_bulk",
        args=(BulkUpdate.model_validate({"issues": "Queue: TEST", "values": {}}),),
        cli=["tracker", "issues", "update-bulk", "--query", "Queue: TEST", "--no-wait"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "bulkchange/_update", json={"issues": "Queue: TEST", "values": {}}),
                Reply(json={"id": "1ac", "status": "CREATED"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.issues.move_bulk",
        args=(
            BulkMove.model_validate(
                {
                    "queue": "CHECK",
                    "issues": ["DE-3"],
                    "values": {"tags": ["moved"]},
                    "moveAllFields": True,
                    "initialStatus": True,
                    "notify": True,
                }
            ),
        ),
        kwargs={"notify": True},
        cli=[
            "tracker",
            "issues",
            "move-bulk",
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
            "tracker_issues_move_bulk",
            {
                "body": {
                    "queue": "CHECK",
                    "issues": ["DE-3"],
                    "values": {"tags": ["moved"]},
                    "moveAllFields": True,
                    "initialStatus": True,
                    "notify": True,
                },
                "notify": True,
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "bulkchange/_move",
                    {"notify": "true"},
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
        "tracker.issues.move_bulk",
        args=(BulkMove.model_validate({"queue": "ARCHIVE", "issues": "Queue: OLD"}),),
        cli=["tracker", "issues", "move-bulk", "ARCHIVE", "--query", "Queue: OLD", "--no-wait"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "bulkchange/_move", json={"queue": "ARCHIVE", "issues": "Queue: OLD"}),
                Reply(json={"id": "2ce", "status": "CREATED"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.issues.transition_bulk",
        args=(
            BulkTransition.model_validate(
                {
                    "transition": "close",
                    "issues": ["DE-4"],
                    "values": {"resolution": "fixed"},
                    "notify": True,
                }
            ),
        ),
        kwargs={"notify": True},
        cli=[
            "tracker",
            "issues",
            "transition-bulk",
            "close",
            "--issue",
            "DE-4",
            "-F",
            "resolution=fixed",
            "--notify",
            "--no-wait",
        ],
        mcp=(
            "tracker_issues_transition_bulk",
            {
                "body": {
                    "transition": "close",
                    "issues": ["DE-4"],
                    "values": {"resolution": "fixed"},
                    "notify": True,
                },
                "notify": True,
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "bulkchange/_transition",
                    {"notify": "true"},
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
        "tracker.issues.transition_bulk",
        args=(BulkTransition.model_validate({"transition": "reopen", "issues": "Queue: QA"}),),
        cli=["tracker", "issues", "transition-bulk", "reopen", "--query", "Queue: QA", "--no-wait"],
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
]
