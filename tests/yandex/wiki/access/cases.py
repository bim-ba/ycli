"""Contract cases for Wiki ``/pages/{id}/access`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.wiki.access.models import PageAccessCreate, PageAccessUpdate


def _grant(access_id: str, role: str, **extra: object) -> dict[str, object]:
    return {"id": access_id, "created_at": "2026-10-02T17:10:49.322Z", "role": role, **extra}


USER = {
    "id": 39185659,
    "identity": {"uid": "9001", "cloud_uid": "cloud-9001"},
    "username": "robot",
    "display_name": "Robot",
    "is_dismissed": False,
    "affiliation": "",
}
GROUP = {
    "id": "7001",
    "identity": {"src": "dir", "id": "7001"},
    "name": "Docs team",
    "type": "group",
    "metadata": {"dir_id": "7001"},
    "members_count": 12,
}
USER_BODY = {
    "user": {"uid": "9001", "cloud_uid": "cloud-9001"},
    "role": "editor",
    "inheritance": "not_inherited",
}
GROUP_BODY = {"group": {"src": "dir", "id": "7002"}, "role": "reader"}
UPDATE_BODY = {"role": "extra_editor", "inheritance": "inherited"}

CASES = [
    Case(
        "wiki.access.create",
        args=(6001, PageAccessCreate.model_validate(USER_BODY)),
        cli=[
            "wiki",
            "access",
            "create",
            "6001",
            "--role",
            "editor",
            "--user-uid",
            "9001",
            "--user-cloud-uid",
            "cloud-9001",
            "--inheritance",
            "not_inherited",
        ],
        mcp=("wiki_access_create", {"page_id": 6001, "body": USER_BODY}),
        exchanges=[
            (
                Sent("POST", "pages/6001/access", json=USER_BODY),
                Reply(json=_grant("5001", "editor", inheritance="not_inherited", user=USER)),
            )
        ],
    ),
    Case(
        "wiki.access.create",
        args=(6002, PageAccessCreate.model_validate(GROUP_BODY)),
        cli=[
            "wiki",
            "access",
            "create",
            "6002",
            "--role",
            "reader",
            "--group-src",
            "dir",
            "--group-id",
            "7002",
        ],
        mcp=("wiki_access_create", {"page_id": 6002, "body": GROUP_BODY}),
        exchanges=[
            (
                Sent("POST", "pages/6002/access", json=GROUP_BODY),
                Reply(json=_grant("5002", "reader", group=GROUP)),
            )
        ],
    ),
    Case(
        "wiki.access.update",
        args=(6003, "5003", PageAccessUpdate.model_validate(UPDATE_BODY)),
        kwargs={"prevent_selflock": True},
        cli=[
            "wiki",
            "access",
            "update",
            "6003",
            "5003",
            "--role",
            "extra_editor",
            "--inheritance",
            "inherited",
            "--prevent-selflock",
        ],
        mcp=(
            "wiki_access_update",
            {"page_id": 6003, "access_id": "5003", "body": UPDATE_BODY, "prevent_selflock": True},
        ),
        effect="idempotent_write",
        exchanges=[
            (
                Sent(
                    "POST",
                    "pages/6003/access/5003",
                    {"prevent_selflock": "true"},
                    json=UPDATE_BODY,
                ),
                Reply(json=_grant("5003", "extra_editor", inheritance="inherited", user=USER)),
            )
        ],
    ),
    Case(
        "wiki.access.update",
        args=(6004, "5004", PageAccessUpdate.model_validate({"inheritance": "not_inherited"})),
        cli=["wiki", "access", "update", "6004", "5004", "--inheritance", "not_inherited"],
        mcp=(
            "wiki_access_update",
            {"page_id": 6004, "access_id": "5004", "body": {"inheritance": "not_inherited"}},
        ),
        effect="idempotent_write",
        exchanges=[
            (
                Sent("POST", "pages/6004/access/5004", json={"inheritance": "not_inherited"}),
                Reply(json=_grant("5004", "reader", inheritance="not_inherited", group=GROUP)),
            )
        ],
    ),
    Case(
        "wiki.access.delete",
        args=(6005, "5005"),
        kwargs={"prevent_selflock": True},
        cli=["wiki", "access", "delete", "6005", "5005", "--prevent-selflock"],
        mcp=(
            "wiki_access_delete",
            {"page_id": 6005, "access_id": "5005", "prevent_selflock": True},
        ),
        exchanges=[
            (
                Sent("DELETE", "pages/6005/access/5005", {"prevent_selflock": "true"}),
                Reply(status=204),
            )
        ],
    ),
    Case(
        "wiki.access.delete",
        args=(6006, "5006"),
        cli=["wiki", "access", "delete", "6006", "5006"],
        mcp=("wiki_access_delete", {"page_id": 6006, "access_id": "5006"}),
        exchanges=[(Sent("DELETE", "pages/6006/access/5006"), Reply(status=204))],
    ),
    Case(
        "wiki.access.clear",
        args=(6007,),
        kwargs={"prevent_selflock": True},
        cli=["wiki", "access", "clear", "6007", "--prevent-selflock"],
        mcp=("wiki_access_clear", {"page_id": 6007, "prevent_selflock": True}),
        exchanges=[
            (Sent("DELETE", "pages/6007/access", {"prevent_selflock": "true"}), Reply(status=204))
        ],
    ),
    Case(
        "wiki.access.clear",
        args=(6008,),
        cli=["wiki", "access", "clear", "6008"],
        mcp=("wiki_access_clear", {"page_id": 6008}),
        exchanges=[(Sent("DELETE", "pages/6008/access"), Reply(status=204))],
    ),
]
