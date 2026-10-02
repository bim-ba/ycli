"""Contract cases for Forms integrations (subscriptions) of a hook (see tests/contract.py)."""

import json
from pathlib import Path

from tests.contract import Case, Reply, Sent
from ycli.yandex.forms.subscriptions.models import SubscriptionAdapter

HERE = Path(__file__).parent
SID = "686d0a1b2c3d4e5f000000b0"
SUBS = f"surveys/{SID}/hooks/21/subscriptions"
EMAIL_FILE = str(HERE / "email.json")
EMAIL = json.loads((HERE / "email.json").read_text(encoding="utf-8"))
HTTP = {
    "type": "http",
    "url": "https://example.com/hook",
    "method": "put",
    "body": "{form.questions_answers_json}",
    "headers": [{"name": "Authorization", "value": "Bearer x", "only_with_value": False}],
    "active": False,
    "follow": False,
}
TRACKER = {
    "type": "tracker",
    "queue": "SUPPORT",
    "subject": "Answer {form.answer_id}",
    "issue_type": 2,
    "priority": 3,
    "fields": [{"key": {"slug": "tags", "type": "string"}, "value": "forms"}],
}


def _read(subscription_id: int, body: dict) -> dict:
    return {**body, "id": subscription_id}


CASES = [
    Case(
        "forms.subscriptions.list",
        args=(SID, 21),
        cli=["forms", "subscriptions", "list", SID, "21"],
        mcp=("forms_subscriptions_list", {"survey_id": SID, "hook_id": 21}),
        exchanges=[
            (Sent("GET", SUBS), Reply(json=[_read(1, HTTP), _read(2, EMAIL), _read(3, TRACKER)]))
        ],
    ),
    Case(
        "forms.subscriptions.get",
        args=(SID, 21, 4),
        cli=["forms", "subscriptions", "get", SID, "21", "4"],
        mcp=("forms_subscriptions_get", {"survey_id": SID, "hook_id": 21, "subscription_id": 4}),
        exchanges=[(Sent("GET", f"{SUBS}/4"), Reply(json=_read(4, TRACKER)))],
    ),
    Case(
        "forms.subscriptions.create",
        args=(SID, 21, SubscriptionAdapter.validate_python(EMAIL)),
        cli=["forms", "subscriptions", "create", SID, "21", "--body-file", EMAIL_FILE],
        mcp=("forms_subscriptions_create", {"survey_id": SID, "hook_id": 21, "body": EMAIL}),
        exchanges=[(Sent("POST", SUBS, json=EMAIL), Reply(json=_read(5, EMAIL)))],
    ),
    Case(
        "forms.subscriptions.modify",
        args=(SID, 21, 6, SubscriptionAdapter.validate_python({**HTTP, "id": 6})),
        cli=None,
        mcp=(
            "forms_subscriptions_update",
            {"survey_id": SID, "hook_id": 21, "subscription_id": 6, "body": {**HTTP, "id": 6}},
        ),
        exchanges=[(Sent("PATCH", f"{SUBS}/6", json=HTTP), Reply(json=_read(6, HTTP)))],
    ),
    Case(
        "forms.subscriptions.modify",
        args=(SID, 21, 7, SubscriptionAdapter.validate_python(EMAIL)),
        cli=["forms", "subscriptions", "update", SID, "21", "7", "--body-file", EMAIL_FILE],
        mcp=None,
        exchanges=[(Sent("PATCH", f"{SUBS}/7", json=EMAIL), Reply(json=_read(7, EMAIL)))],
    ),
    Case(
        "forms.subscriptions.delete",
        args=(SID, 21, 8),
        cli=["forms", "subscriptions", "delete", SID, "21", "8"],
        mcp=("forms_subscriptions_delete", {"survey_id": SID, "hook_id": 21, "subscription_id": 8}),
        exchanges=[(Sent("DELETE", f"{SUBS}/8"), Reply())],
    ),
    Case(
        "forms.subscriptions.attach",
        args=(SID, 21, 9),
        kwargs={"filename": "terms.pdf", "data": b"%PDF-1.4 terms\n"},
        cli=["forms", "subscriptions", "attach", SID, "21", "9", str(HERE / "terms.pdf")],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    f"{SUBS}/9/attachment",
                    files={"file": ("terms.pdf", b"%PDF-1.4 terms\n")},
                ),
                Reply(json={"name": "terms.pdf", "path": "/forms/terms.pdf", "size": 15}),
            )
        ],
    ),
]
