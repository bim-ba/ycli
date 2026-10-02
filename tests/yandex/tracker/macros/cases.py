"""Contract cases for Tracker queue ``/macros`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.macros.models import MacroCreate, MacroUpdate

CASES = [
    Case(
        "tracker.macros.list",
        args=("TEST",),
        cli=["tracker", "macros", "list", "TEST"],
        mcp=("tracker_macros_list", {"queue_id": "TEST"}),
        exchanges=[(Sent("GET", "queues/TEST/macros"), Reply(json=[{"id": 3, "name": "Close"}]))],
    ),
    Case(
        "tracker.macros.get",
        args=("OPS", 4),
        cli=["tracker", "macros", "get", "OPS", "4"],
        mcp=("tracker_macros_get", {"queue_id": "OPS", "macro_id": 4}),
        exchanges=[(Sent("GET", "queues/OPS/macros/4"), Reply(json={"id": 4, "name": "Escalate"}))],
    ),
    Case(
        "tracker.macros.create",
        args=(
            "DEV",
            MacroCreate(name="Triage", body="Taking a look", issue_update={"tags": {"add": "x"}}),
        ),
        cli=[
            "tracker",
            "macros",
            "create",
            "DEV",
            "--name",
            "Triage",
            "--body",
            "Taking a look",
            "--issue-update",
            '{"tags": {"add": "x"}}',
        ],
        mcp=(
            "tracker_macros_create",
            {
                "queue_id": "DEV",
                "body": {
                    "name": "Triage",
                    "body": "Taking a look",
                    "issue_update": {"tags": {"add": "x"}},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "queues/DEV/macros",
                    json={
                        "name": "Triage",
                        "body": "Taking a look",
                        "issueUpdate": {"tags": {"add": "x"}},
                    },
                ),
                Reply(json={"id": 5, "name": "Triage"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.macros.edit",
        args=(
            "QA",
            6,
            MacroUpdate(name="Renamed", body="New text", issue_update={"priority": "critical"}),
        ),
        cli=[
            "tracker",
            "macros",
            "edit",
            "QA",
            "6",
            "--name",
            "Renamed",
            "--body",
            "New text",
            "--issue-update",
            '{"priority": "critical"}',
        ],
        mcp=(
            "tracker_macros_edit",
            {
                "queue_id": "QA",
                "macro_id": 6,
                "body": {
                    "name": "Renamed",
                    "body": "New text",
                    "issue_update": {"priority": "critical"},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "queues/QA/macros/6",
                    json={
                        "name": "Renamed",
                        "body": "New text",
                        "issueUpdate": {"priority": "critical"},
                    },
                ),
                Reply(json={"id": 6, "name": "Renamed"}),
            )
        ],
    ),
    Case(
        "tracker.macros.delete",
        args=("SUP", 7),
        cli=["tracker", "macros", "delete", "SUP", "7"],
        mcp=("tracker_macros_delete", {"queue_id": "SUP", "macro_id": 7}),
        exchanges=[(Sent("DELETE", "queues/SUP/macros/7"), Reply(status=204))],
    ),
]
