"""TDD for the triggers models — polymorphic actions/conditions round-trip via extra=allow."""

from ycli.yandex.tracker.triggers.models import (
    Trigger,
    TriggerAction,
    TriggerCondition,
    TriggerCreate,
    TriggerUpdate,
    WebhookLogEntry,
    WebhookLogList,
)


def test_trigger_parses_full_payload():
    t = Trigger.model_validate(
        {
            "id": 16,
            "self": "https://api.tracker.yandex.net/v3/queues/DESIGN/triggers/16",
            "queue": {"id": "26", "key": "DESIGN", "display": "Design"},
            "name": "trigger_name",
            "order": "0.0002",
            "actions": [{"type": "Transition", "id": 1, "status": {"key": "needInfo"}}],
            "conditions": [{"type": "Or", "conditions": [{"type": "Event.comment-create"}]}],
            "version": 1,
            "active": True,
        }
    )
    assert t.id == 16 and t.queue.key == "DESIGN" and t.active is True  # ty: ignore[unresolved-attribute]
    assert t.actions[0].type == "Transition"
    # extra polymorphic keys survive on the read side
    assert t.actions[0].model_dump()["status"] == {"key": "needInfo"}
    assert t.conditions[0].type == "Or"
    assert t.conditions[0].conditions[0].type == "Event.comment-create"  # ty: ignore[not-subscriptable]


def test_action_and_condition_preserve_extra_fields():
    action = TriggerAction.model_validate(
        {"type": "Webhook", "endpoint": "https://x", "method": "GET"}
    )
    assert action.model_dump(exclude_none=True) == {
        "type": "Webhook",
        "endpoint": "https://x",
        "method": "GET",
    }
    cond = TriggerCondition.model_validate(
        {"type": "CommentFullyMatchCondition", "word": "Open", "ignoreCase": True}
    )
    assert cond.model_dump(exclude_none=True) == {
        "type": "CommentFullyMatchCondition",
        "word": "Open",
        "ignoreCase": True,
    }


def test_trigger_create_body_serializes_actions_and_conditions():
    body = TriggerCreate(
        name="TriggerName",
        actions=[TriggerAction(type="Transition", status={"key": "open"})],  # ty: ignore[unknown-argument]
        conditions=[TriggerCondition(type="CommentFullyMatchCondition", word="Open")],  # ty: ignore[unknown-argument]
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "name": "TriggerName",
        "actions": [{"type": "Transition", "status": {"key": "open"}}],
        "conditions": [{"type": "CommentFullyMatchCondition", "word": "Open"}],
    }


def test_trigger_update_only_supplied_fields():
    assert TriggerUpdate(active=False).model_dump(by_alias=True, exclude_none=True) == {
        "active": False
    }
    assert TriggerUpdate(before=6, active=True).model_dump(by_alias=True, exclude_none=True) == {
        "before": 6,
        "active": True,
    }


def test_webhook_log_entry_aliases():
    entry = WebhookLogEntry.model_validate(
        {"id": "x", "startTime": "2025", "triggerId": 123, "actionId": 1, "duration": 235}
    )
    assert entry.start_time == "2025" and entry.trigger_id == 123 and entry.action_id == 1
    assert WebhookLogList.model_validate([{"id": "x"}]).root[0].id == "x"
