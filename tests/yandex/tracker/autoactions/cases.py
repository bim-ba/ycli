"""Contract cases for Tracker queue ``/autoactions`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.autoactions.models import AutoactionCalendar, AutoactionCreate
from ycli.yandex.tracker.models import AutomationAction

NEED_INFO = {"type": "Transition", "status": {"key": "needInfo"}}
NOTIFY = {"type": "Webhook", "endpoint": "https://hooks.example.com/aa"}

CASES = [
    Case(
        "tracker.autoactions.get",
        args=("DESIGN", 9),
        cli=["tracker", "autoactions", "get", "DESIGN", "9"],
        mcp=("tracker_autoactions_get", {"queue_id": "DESIGN", "action_id": 9}),
        exchanges=[
            (
                Sent("GET", "queues/DESIGN/autoactions/9"),
                Reply(json={"id": 9, "name": "Nightly", "actions": [NEED_INFO]}),
            )
        ],
    ),
    Case(
        "tracker.autoactions.create",
        args=(
            "OPS",
            AutoactionCreate(
                name="Stale sweep",
                query="Status: Open",
                filter={"priority": "minor"},
                actions=[
                    AutomationAction.model_validate(NEED_INFO),
                    AutomationAction.model_validate(NOTIFY),
                ],
                active=False,
                enable_notifications=True,
                interval_millis=7200000,
                calendar=AutoactionCalendar(id=2),
            ),
        ),
        cli=[
            "tracker",
            "autoactions",
            "create",
            "OPS",
            "--name",
            "Stale sweep",
            "--query",
            "Status: Open",
            "--filter",
            '{"priority": "minor"}',
            "--action",
            '{"type": "Transition", "status": {"key": "needInfo"}}',
            "--action",
            '{"type": "Webhook", "endpoint": "https://hooks.example.com/aa"}',
            "--inactive",
            "--notify",
            "--interval-millis",
            "7200000",
            "--calendar-id",
            "2",
        ],
        mcp=(
            "tracker_autoactions_create",
            {
                "queue_id": "OPS",
                "body": {
                    "name": "Stale sweep",
                    "query": "Status: Open",
                    "filter": {"priority": "minor"},
                    "actions": [NEED_INFO, NOTIFY],
                    "active": False,
                    "enable_notifications": True,
                    "interval_millis": 7200000,
                    "calendar": {"id": 2},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "queues/OPS/autoactions",
                    json={
                        "name": "Stale sweep",
                        "filter": {"priority": "minor"},
                        "query": "Status: Open",
                        "actions": [
                            {"type": "Transition", "status": {"key": "needInfo"}},
                            {"type": "Webhook", "endpoint": "https://hooks.example.com/aa"},
                        ],
                        "active": False,
                        "enableNotifications": True,
                        "intervalMillis": 7200000,
                        "calendar": {"id": 2},
                    },
                ),
                Reply(json={"id": 10, "name": "Stale sweep"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.autoactions.logs_list",
        args=("QA", 11),
        cli=["tracker", "autoactions", "logs-list", "QA", "11"],
        mcp=("tracker_autoactions_logs_list", {"queue_id": "QA", "action_id": 11}),
        exchanges=[
            (
                Sent("GET", "queues/QA/autoactions/11/logs"),
                Reply(json=[{"id": "run-1", "searchHits": 3}]),
            )
        ],
    ),
    Case(
        "tracker.autoactions.logs_get",
        args=("SUP", 12, "run-2"),
        cli=["tracker", "autoactions", "logs-get", "SUP", "12", "run-2"],
        mcp=(
            "tracker_autoactions_logs_get",
            {"queue_id": "SUP", "action_id": 12, "run_id": "run-2"},
        ),
        exchanges=[
            (
                Sent("GET", "queues/SUP/autoactions/12/logs/run-2"),
                Reply(
                    json=[
                        {
                            "id": 0,
                            "issueReference": {"key": "SUP-1"},
                            "status": {"value": "success"},
                        }
                    ]
                ),
            )
        ],
    ),
]
