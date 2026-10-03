"""Forms integration-group (hook) models parse what the live API returns."""

from ycli.yandex.forms.hooks.models import Hook, HookCreate, HookUpdate
from ycli.yandex.forms.subscriptions.models import HttpSubscription
from ycli.yandex.models import ItemList

# As GET /surveys/{id}/hooks/{hook_id} answered on the test organization (2026-10-02).
LIVE = {
    "id": 18746511,
    "name": "probe",
    "active": False,
    "subscriptions": [
        {
            "type": "http",
            "url": "https://example.invalid/hook",
            "method": "post",
            "body": "",
            "id": 19059006,
            "active": False,
            "follow": False,
        }
    ],
}


def test_hook_parses_live_answer_with_typed_subscriptions():
    hook = Hook.model_validate(LIVE)
    assert hook.id == 18746511 and hook.active is False and hook.conditions is None
    assert isinstance(hook.subscriptions[0], HttpSubscription)
    assert hook.subscriptions[0].method == "post"


def test_hook_keeps_its_conditions():
    hook = Hook.model_validate(
        {"id": 1, "conditions": {"operator": "or", "items": [{"id": 9, "operator": "and"}]}}
    )
    assert hook.conditions is not None and hook.conditions.items[0].id == 9


def test_hook_list_wraps_bare_array():
    assert [h.id for h in ItemList[Hook].model_validate([LIVE, {"id": 2}]).root] == [18746511, 2]


def test_hook_bodies_drop_unset_fields():
    assert HookCreate(name="CRM").model_dump(exclude_none=True) == {"name": "CRM"}
    assert HookUpdate(active=True).model_dump(exclude_none=True) == {"active": True}
