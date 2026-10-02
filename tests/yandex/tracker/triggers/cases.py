"""Contract cases for Tracker queue ``/triggers`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.triggers.models import (
    TriggerAction,
    TriggerCondition,
    TriggerCreate,
    TriggerUpdate,
)

TRANSITION = {"type": "Transition", "status": {"key": "open"}}
COMMENT = {"type": "CreateComment", "text": "Reopened"}
MATCH = {"type": "CommentFullyMatchCondition", "word": "Open"}

CASES = [
    Case(
        "tracker.triggers.get",
        args=("DESIGN", 16),
        cli=["tracker", "triggers", "get", "DESIGN", "16"],
        mcp=("tracker_triggers_get", {"queue_id": "DESIGN", "trigger_id": 16}),
        exchanges=[
            (
                Sent("GET", "queues/DESIGN/triggers/16"),
                Reply(json={"id": 16, "name": "On comment", "actions": [TRANSITION]}),
            )
        ],
    ),
    Case(
        "tracker.triggers.create",
        args=(
            "ART",
            TriggerCreate(
                name="Reopen on comment",
                actions=[
                    TriggerAction.model_validate(TRANSITION),
                    TriggerAction.model_validate(COMMENT),
                ],
                conditions=[TriggerCondition.model_validate(MATCH)],
                active=False,
            ),
        ),
        cli=[
            "tracker",
            "triggers",
            "create",
            "ART",
            "--name",
            "Reopen on comment",
            "--action",
            '{"type": "Transition", "status": {"key": "open"}}',
            "--action",
            '{"type": "CreateComment", "text": "Reopened"}',
            "--condition",
            '{"type": "CommentFullyMatchCondition", "word": "Open"}',
            "--inactive",
        ],
        mcp=(
            "tracker_triggers_create",
            {
                "queue_id": "ART",
                "body": {
                    "name": "Reopen on comment",
                    "actions": [TRANSITION, COMMENT],
                    "conditions": [MATCH],
                    "active": False,
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "queues/ART/triggers",
                    json={
                        "name": "Reopen on comment",
                        "actions": [
                            {"type": "Transition", "status": {"key": "open"}},
                            {"type": "CreateComment", "text": "Reopened"},
                        ],
                        "conditions": [{"type": "CommentFullyMatchCondition", "word": "Open"}],
                        "active": False,
                    },
                ),
                Reply(json={"id": 17, "name": "Reopen on comment"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.triggers.edit",
        args=(
            "BIZ",
            18,
            TriggerUpdate(
                name="Renamed trigger",
                actions=[TriggerAction.model_validate(COMMENT)],
                conditions=[TriggerCondition.model_validate(MATCH)],
                active=True,
            ),
        ),
        kwargs={"version": 3},
        cli=[
            "tracker",
            "triggers",
            "update",
            "BIZ",
            "18",
            "--name",
            "Renamed trigger",
            "--action",
            '{"type": "CreateComment", "text": "Reopened"}',
            "--condition",
            '{"type": "CommentFullyMatchCondition", "word": "Open"}',
            "--active",
            "--version",
            "3",
        ],
        mcp=(
            "tracker_triggers_update",
            {
                "queue_id": "BIZ",
                "trigger_id": 18,
                "body": {
                    "name": "Renamed trigger",
                    "actions": [COMMENT],
                    "conditions": [MATCH],
                    "active": True,
                },
                "version": 3,
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "queues/BIZ/triggers/18",
                    {"version": "3"},
                    {
                        "name": "Renamed trigger",
                        "actions": [{"type": "CreateComment", "text": "Reopened"}],
                        "conditions": [{"type": "CommentFullyMatchCondition", "word": "Open"}],
                        "active": True,
                    },
                ),
                Reply(json={"id": 18, "name": "Renamed trigger"}),
            )
        ],
    ),
    # Without a version (the CLI's 0) no ?version= is sent.
    Case(
        "tracker.triggers.edit",
        args=("CRM", 19, TriggerUpdate(active=False)),
        cli=["tracker", "triggers", "update", "CRM", "19", "--inactive"],
        mcp=(
            "tracker_triggers_update",
            {"queue_id": "CRM", "trigger_id": 19, "body": {"active": False}},
        ),
        exchanges=[
            (
                Sent("PATCH", "queues/CRM/triggers/19", json={"active": False}),
                Reply(json={"id": 19, "active": False}),
            )
        ],
    ),
    # `before` (the trigger's place in the order) is an MCP/SDK-only field.
    Case(
        "tracker.triggers.edit",
        args=("HR", 20, TriggerUpdate(before=12)),
        kwargs={"version": 9},
        cli=None,
        mcp=(
            "tracker_triggers_update",
            {"queue_id": "HR", "trigger_id": 20, "body": {"before": 12}, "version": 9},
        ),
        exchanges=[
            (
                Sent("PATCH", "queues/HR/triggers/20", {"version": "9"}, {"before": 12}),
                Reply(json={"id": 20, "order": "0.5"}),
            )
        ],
    ),
    Case(
        "tracker.triggers.webhook_log",
        args=("DEV", 6),
        kwargs={
            "issue_id": "DEV-5",
            "limit": 100,
            "date_from": "2026-01-01T00:00:00.000+0300",
            "date_to": "2026-02-01T00:00:00.000+0300",
        },
        cli=[
            "tracker",
            "triggers",
            "webhook-log-list",
            "DEV",
            "6",
            "--issue-id",
            "DEV-5",
            "--limit",
            "100",
            "--from",
            "2026-01-01T00:00:00.000+0300",
            "--to",
            "2026-02-01T00:00:00.000+0300",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "GET",
                    "queues/DEV/triggers/6/webhooks/log",
                    {
                        "issueId": "DEV-5",
                        "limit": "100",
                        "from": "2026-01-01T00:00:00.000+0300",
                        "to": "2026-02-01T00:00:00.000+0300",
                    },
                ),
                Reply(json=[{"id": "x", "duration": 235}]),
            )
        ],
    ),
    Case(
        "tracker.triggers.webhook_log",
        args=("MKT", 7),
        kwargs={"issue_id": "MKT-8", "limit": 25},
        cli=[
            "tracker",
            "triggers",
            "webhook-log-list",
            "MKT",
            "7",
            "--issue-id",
            "MKT-8",
            "--limit",
            "25",
        ],
        mcp=(
            "tracker_triggers_webhook_log_list",
            {"queue_id": "MKT", "trigger_id": 7, "issue_id": "MKT-8", "limit": 25},
        ),
        exchanges=[
            (
                Sent(
                    "GET", "queues/MKT/triggers/7/webhooks/log", {"issueId": "MKT-8", "limit": "25"}
                ),
                Reply(json=[{"id": "y", "duration": 12}]),
            )
        ],
    ),
    Case(
        "tracker.triggers.webhook_log",
        args=("LAB", 8),
        cli=["tracker", "triggers", "webhook-log-list", "LAB", "8"],
        mcp=("tracker_triggers_webhook_log_list", {"queue_id": "LAB", "trigger_id": 8}),
        exchanges=[(Sent("GET", "queues/LAB/triggers/8/webhooks/log"), Reply(json=[]))],
    ),
    # The default cap asks for 50-row pages and walks id=<last trigger id> until a page is empty.
    Case(
        "tracker.triggers.list",
        args=("LISTQ",),
        kwargs={"limit": 500},
        cli=["tracker", "triggers", "list", "LISTQ"],
        mcp=("tracker_triggers_list", {"queue_id": "LISTQ"}),
        exchanges=[
            (
                Sent("GET", "queues/LISTQ/triggers", {"perPage": "50"}),
                Reply(
                    json=[
                        {"id": 21, "name": "First", "version": 1, "active": True},
                        {"id": 22, "name": "Second", "actions": [TRANSITION], "active": False},
                    ]
                ),
            ),
            (Sent("GET", "queues/LISTQ/triggers", {"perPage": "50", "id": "22"}), Reply(json=[])),
        ],
    ),
    # A small cap narrows the page to the cap and stops after it.
    Case(
        "tracker.triggers.list",
        args=("CAPQ",),
        kwargs={"limit": 2},
        cli=["tracker", "triggers", "list", "CAPQ", "--limit", "2"],
        mcp=("tracker_triggers_list", {"queue_id": "CAPQ", "limit": 2}),
        exchanges=[
            (
                Sent("GET", "queues/CAPQ/triggers", {"perPage": "2"}),
                Reply(json=[{"id": 31, "name": "A"}, {"id": 32, "name": "B"}]),
            )
        ],
    ),
    Case(
        "tracker.triggers.list",
        args=("ALLQ",),
        cli=["tracker", "triggers", "list", "ALLQ", "--all"],
        mcp=None,
        exchanges=[(Sent("GET", "queues/ALLQ/triggers", {"perPage": "50"}), Reply(json=[]))],
    ),
]
