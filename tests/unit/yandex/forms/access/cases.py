"""Contract cases for Forms ``/surveys/{id}/access`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.forms.access.models import AccessGrant, AccessRevoke, AccessUpdate

SID = "686d0a1b2c3d4e5f000000d0"
ACCESS = f"surveys/{SID}/access"
# As GET /surveys/{id}/access answered on the test organization (2026-10-02), plus a group.
PERMISSIONS = [
    {
        "access": "restricted",
        "action": "change",
        "users": [
            {
                "identity": {"uid": "101523906", "cloud_uid": "ajen8nffceu4rqs0i39r"},
                "username": "znatnov-sava",
                "display_name": "Сава Знатнов",
            }
        ],
        "groups": [{"identity": {"src": "dir", "id": "5"}, "name": "Support", "type": "group"}],
    },
    {"access": "common", "action": "submit"},
]
USER = {"uid": "7001", "cloud_uid": "cloud-7001"}
GROUP = {"src": "staff", "id": "42"}

CASES = [
    Case(
        "forms.access.list",
        args=(SID,),
        cli=["forms", "access", "list", SID],
        mcp=("forms_access_list", {"survey_id": SID}),
        exchanges=[(Sent("GET", ACCESS), Reply(json=PERMISSIONS))],
    ),
    Case(
        "forms.access.update",
        args=(SID, AccessUpdate.model_validate({"action": "submit", "access": "public"})),
        cli=["forms", "access", "update", SID, "--action", "submit", "--access", "public"],
        mcp=(
            "forms_access_update",
            {"survey_id": SID, "body": {"action": "submit", "access": "public"}},
        ),
        exchanges=[
            (
                Sent("POST", ACCESS, json={"action": "submit", "access": "public"}),
                Reply(json=PERMISSIONS),
            )
        ],
        effect=Effect.IDEMPOTENT_WRITE,
    ),
    Case(
        "forms.access.grant",
        args=(SID, AccessGrant.model_validate({"action": "change", "user": USER})),
        cli=[
            "forms",
            "access",
            "grant",
            SID,
            "--action",
            "change",
            "--uid",
            "7001",
            "--cloud-uid",
            "cloud-7001",
        ],
        mcp=("forms_access_grant", {"survey_id": SID, "body": {"action": "change", "user": USER}}),
        exchanges=[
            (
                Sent("POST", f"{ACCESS}/grant", json={"action": "change", "user": USER}),
                Reply(json=PERMISSIONS),
            )
        ],
        effect=Effect.IDEMPOTENT_WRITE,
    ),
    Case(
        "forms.access.grant",
        args=(SID, AccessGrant.model_validate({"action": "submit", "group": GROUP})),
        cli=[
            "forms",
            "access",
            "grant",
            SID,
            "--action",
            "submit",
            "--group-src",
            "staff",
            "--group-id",
            "42",
        ],
        mcp=None,
        exchanges=[
            (
                Sent("POST", f"{ACCESS}/grant", json={"action": "submit", "group": GROUP}),
                Reply(json=PERMISSIONS),
            )
        ],
        effect=Effect.IDEMPOTENT_WRITE,
    ),
    Case(
        "forms.access.revoke",
        args=(SID, AccessRevoke.model_validate({"action": "submit", "group": GROUP})),
        cli=[
            "forms",
            "access",
            "revoke",
            SID,
            "--action",
            "submit",
            "--group-src",
            "staff",
            "--group-id",
            "42",
        ],
        mcp=(
            "forms_access_revoke",
            {"survey_id": SID, "body": {"action": "submit", "group": GROUP}},
        ),
        exchanges=[
            (
                Sent("POST", f"{ACCESS}/revoke", json={"action": "submit", "group": GROUP}),
                Reply(json=PERMISSIONS),
            )
        ],
        effect=Effect.DESTRUCTIVE,
    ),
    Case(
        "forms.access.revoke",
        args=(SID, AccessRevoke.model_validate({"action": "change", "user": {"uid": "7002"}})),
        cli=["forms", "access", "revoke", SID, "--action", "change", "--uid", "7002"],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST", f"{ACCESS}/revoke", json={"action": "change", "user": {"uid": "7002"}}
                ),
                Reply(json=PERMISSIONS),
            )
        ],
        effect=Effect.DESTRUCTIVE,
    ),
]
