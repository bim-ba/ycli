"""Forms integration (subscription) models: the union picks the member by ``type``."""

import pytest
from pydantic import ValidationError

from ycli.yandex.forms.subscriptions.models import (
    EmailSubscription,
    FunctionSubscription,
    HttpSubscription,
    JsonRpcSubscription,
    Subscription,
    SubscriptionAdapter,
    TrackerCommentSubscription,
    TrackerFieldKey,
    TrackerSubscription,
    WikiGrid,
    WikiSubscription,
)
from ycli.yandex.models import ItemList


@pytest.mark.parametrize(
    ("body", "member"),
    [
        ({"type": "email", "email_to_address": "a@example.com"}, EmailSubscription),
        ({"type": "tracker", "queue": "SUP"}, TrackerSubscription),
        ({"type": "tracker_comment", "issue": "SUP-1"}, TrackerCommentSubscription),
        ({"type": "wiki", "supertag": "team/answers"}, WikiSubscription),
        ({"type": "jsonrpc", "method": "answers.add"}, JsonRpcSubscription),
        ({"type": "http", "url": "https://example.com"}, HttpSubscription),
        ({"type": "function", "function_id": "d4e1"}, FunctionSubscription),
    ],
)
def test_union_picks_member_by_type(body, member):
    assert isinstance(SubscriptionAdapter.validate_python(body), member)


def test_an_unknown_type_is_refused():
    with pytest.raises(ValidationError):
        SubscriptionAdapter.validate_python({"type": "carrier-pigeon"})


def test_live_http_subscription_and_rich_members_parse():
    # The http member as POST …/subscriptions answered on the test organization (2026-10-02).
    live = {
        "type": "http",
        "url": "https://example.invalid/hook",
        "method": "post",
        "body": "",
        "id": 19059006,
        "active": False,
        "follow": False,
    }
    tracker = {
        "type": "tracker",
        "fields": [{"key": {"slug": "tags", "name": "Теги", "type": "string"}, "value": "x"}],
        "attachments": {"question": {"all": True}, "static": [{"id": 3, "name": "a.pdf"}]},
    }
    wiki = {
        "type": "wiki",
        "grid_data": {"grid_id": "g1", "cols": [{"key": {"slug": "n", "type": "string"}}]},
    }
    first, second, third = ItemList[Subscription].model_validate([live, tracker, wiki]).root
    assert first.id == 19059006
    assert isinstance(second, TrackerSubscription) and second.fields and second.attachments
    assert isinstance(second.fields[0].key, TrackerFieldKey)
    assert second.attachments.static and second.attachments.static[0].name == "a.pdf"
    assert isinstance(third, WikiSubscription) and isinstance(third.grid_data, WikiGrid)


def test_a_member_dumps_its_type_tag():
    assert HttpSubscription(active=False).model_dump(exclude_none=True) == {
        "type": "http",
        "active": False,
    }
