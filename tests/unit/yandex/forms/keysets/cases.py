"""Contract cases for Forms ``/surveys/{id}/keysets`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.forms.keysets.models import KeysetCreate, KeysetUpdate

SID = "686d0a1b2c3d4e5f00000020"
KEYSETS = f"surveys/{SID}/keysets"
KEYSET = {"id": 3, "name": "Q1 invites", "total": 100, "is_enabled": True}

CASES = [
    Case(
        "forms.keysets.list",
        args=(SID,),
        cli=["forms", "keysets", "list", SID],
        mcp=("forms_keysets_list", {"survey_id": SID}),
        exchanges=[(Sent("GET", KEYSETS), Reply(json=[KEYSET]))],
    ),
    Case(
        "forms.keysets.get",
        args=(SID, 3),
        cli=["forms", "keysets", "get", SID, "3"],
        mcp=("forms_keysets_get", {"survey_id": SID, "keyset_id": 3}),
        exchanges=[(Sent("GET", f"{KEYSETS}/3"), Reply(json=KEYSET))],
    ),
    Case(
        "forms.keysets.create",
        args=(
            SID,
            KeysetCreate.model_validate({"name": "Q1 invites", "total": 100, "is_enabled": True}),
        ),
        cli=[
            "forms",
            "keysets",
            "create",
            SID,
            "--name",
            "Q1 invites",
            "--total",
            "100",
            "--enabled",
        ],
        mcp=(
            "forms_keysets_create",
            {"survey_id": SID, "body": {"name": "Q1 invites", "total": 100, "is_enabled": True}},
        ),
        exchanges=[
            (
                Sent(
                    "POST", KEYSETS, json={"name": "Q1 invites", "total": 100, "is_enabled": True}
                ),
                Reply(json=KEYSET, status=201),
            )
        ],
    ),
    Case(
        "forms.keysets.update",
        args=(
            SID,
            4,
            KeysetUpdate.model_validate({"name": "Q2 invites", "total": 7, "is_enabled": False}),
        ),
        cli=[
            "forms",
            "keysets",
            "update",
            SID,
            "4",
            "--name",
            "Q2 invites",
            "--total",
            "7",
            "--disabled",
        ],
        mcp=(
            "forms_keysets_update",
            {
                "survey_id": SID,
                "keyset_id": 4,
                "body": {"name": "Q2 invites", "total": 7, "is_enabled": False},
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    f"{KEYSETS}/4",
                    json={"name": "Q2 invites", "total": 7, "is_enabled": False},
                ),
                Reply(json=KEYSET),
            )
        ],
    ),
    Case(
        "forms.keysets.delete",
        args=(SID, 5),
        cli=["forms", "keysets", "delete", SID, "5"],
        mcp=("forms_keysets_delete", {"survey_id": SID, "keyset_id": 5}),
        exchanges=[(Sent("DELETE", f"{KEYSETS}/5"), Reply())],
    ),
    Case(
        "forms.keysets.download",
        args=(SID, 6),
        cli=["forms", "keysets", "download", SID, "6"],
        mcp=None,
        exchanges=[(Sent("GET", f"{KEYSETS}/6/download"), Reply(content=b"key-1\nkey-2\n"))],
    ),
]
