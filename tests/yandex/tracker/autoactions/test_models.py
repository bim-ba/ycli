"""TDD for the autoactions models — the two log shapes and the typed create body."""

from ycli.yandex.tracker.autoactions.models import (
    Autoaction,
    AutoactionAction,
    AutoactionCalendar,
    AutoactionCreate,
    AutoactionLogEntry,
    AutoactionLogList,
    AutoactionRunEntry,
    AutoactionRunList,
)


def test_autoaction_parses_full_payload():
    a = Autoaction.model_validate(
        {
            "id": 9,
            "self": "https://api.tracker.yandex.net/v3/queues/DESIGN/autoactions/9",
            "queue": {"id": "26", "key": "DESIGN", "display": "Design"},
            "name": "autoaction_name",
            "version": 4,
            "active": True,
            "filter": {"priority": ["critical"]},
            "actions": [{"type": "Transition", "id": 1, "status": {"key": "needInfo"}}],
            "enableNotifications": False,
            "totalIssuesProcessed": 0,
            "intervalMillis": 3600000,
            "calendar": {"id": 2},
        }
    )
    assert a.id == 9 and a.queue.key == "DESIGN" and a.active is True  # ty: ignore[unresolved-attribute]
    assert a.filter == {"priority": ["critical"]}
    assert a.actions[0].type == "Transition"
    assert a.enable_notifications is False and a.interval_millis == 3600000
    assert a.total_issues_processed == 0 and a.calendar.id == 2  # ty: ignore[unresolved-attribute]


def test_autoaction_create_serializes_aliases():
    body = AutoactionCreate(
        name="A",
        filter={"priority": ["critical"]},
        actions=[AutoactionAction(type="Transition", status={"key": "needInfo"})],  # ty: ignore[unknown-argument]
        enable_notifications=False,
        interval_millis=3600000,
        calendar=AutoactionCalendar(id=2),
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "name": "A",
        "filter": {"priority": ["critical"]},
        "actions": [{"type": "Transition", "status": {"key": "needInfo"}}],
        "enableNotifications": False,
        "intervalMillis": 3600000,
        "calendar": {"id": 2},
    }


def test_autoaction_create_with_query():
    body = AutoactionCreate(
        name="A", query="Status: Open", actions=[AutoactionAction(type="Transition")]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body["query"] == "Status: Open"


def test_log_entry_and_list():
    entry = AutoactionLogEntry.model_validate(
        {"id": "x", "launchTime": "2025", "searchHits": 3, "successes": 3, "searchFailed": False}
    )
    assert entry.launch_time == "2025" and entry.search_hits == 3 and entry.search_failed is False
    assert AutoactionLogList.model_validate([{"id": "x"}]).root[0].id == "x"


def test_run_entry_and_list():
    entry = AutoactionRunEntry.model_validate(
        {
            "id": 0,
            "issueReference": {"key": "TEST-1", "version": 0},
            "status": {"value": "success", "display": "Success"},
        }
    )
    assert entry.id == 0 and entry.issue_reference.key == "TEST-1"  # ty: ignore[unresolved-attribute]
    assert entry.status.value == "success"  # ty: ignore[unresolved-attribute]
    assert AutoactionRunList.model_validate([{"id": 0}]).root[0].id == 0
