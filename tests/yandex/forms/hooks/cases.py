"""Contract cases for Forms ``/surveys/{id}/hooks`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

SID = "686d0a1b2c3d4e5f000000a0"
HOOKS = f"surveys/{SID}/hooks"


def _hook(hook_id: int) -> dict:
    return {
        "id": hook_id,
        "name": "CRM",
        "active": False,
        "conditions": {
            "operator": "or",
            "items": [
                {
                    "id": 91,
                    "operator": "and",
                    "items": [
                        {"type": "question", "condition": "eq", "question": "q1", "value": "y"}
                    ],
                }
            ],
        },
        "subscriptions": [
            {
                "type": "http",
                "url": "https://example.com/hook",
                "method": "post",
                "body": "",
                "id": 4,
                "active": False,
                "follow": False,
            }
        ],
    }


CASES = [
    Case(
        "forms.hooks.list",
        args=(SID,),
        cli=["forms", "hooks", "list", SID],
        mcp=("forms_hooks_list", {"survey_id": SID}),
        exchanges=[(Sent("GET", HOOKS), Reply(json=[_hook(11)]))],
    ),
    Case(
        "forms.hooks.get",
        args=(SID, 12),
        cli=["forms", "hooks", "get", SID, "12"],
        mcp=("forms_hooks_get", {"survey_id": SID, "hook_id": 12}),
        exchanges=[(Sent("GET", f"{HOOKS}/12"), Reply(json=_hook(12)))],
    ),
    Case(
        "forms.hooks.create",
        args=(SID, {"name": "CRM", "active": False}),
        cli=["forms", "hooks", "create", SID, "--name", "CRM", "--inactive"],
        mcp=("forms_hooks_create", {"survey_id": SID, "body": {"name": "CRM", "active": False}}),
        exchanges=[
            (Sent("POST", HOOKS, json={"name": "CRM", "active": False}), Reply(json=_hook(13)))
        ],
    ),
    Case(
        "forms.hooks.create",
        args=(SID, {}),
        cli=["forms", "hooks", "create", SID],
        mcp=None,
        exchanges=[(Sent("POST", HOOKS, json={}), Reply(json=_hook(14)))],
    ),
    Case(
        "forms.hooks.modify",
        args=(SID, 15, {"name": "Helpdesk", "active": True}),
        cli=["forms", "hooks", "update", SID, "15", "--name", "Helpdesk", "--active"],
        mcp=(
            "forms_hooks_update",
            {"survey_id": SID, "hook_id": 15, "body": {"name": "Helpdesk", "active": True}},
        ),
        exchanges=[
            (
                Sent("PATCH", f"{HOOKS}/15", json={"name": "Helpdesk", "active": True}),
                Reply(json=_hook(15)),
            )
        ],
    ),
    Case(
        "forms.hooks.delete",
        args=(SID, 16),
        cli=["forms", "hooks", "delete", SID, "16"],
        mcp=("forms_hooks_delete", {"survey_id": SID, "hook_id": 16}),
        exchanges=[(Sent("DELETE", f"{HOOKS}/16"), Reply())],
    ),
]
