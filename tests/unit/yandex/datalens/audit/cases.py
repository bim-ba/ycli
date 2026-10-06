"""Contract cases for DataLens audit (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

# The keys of a live reply (2026-10-06).
CHANGED = {
    "entryId": "ent0000000001",
    "key": None,
    "isDeleted": False,
    "workbookId": "wb000000000001",
    "collectionId": None,
    "parentFolderId": None,
    "scope": "dataset",
    "type": "",
    "updatedAt": "2026-10-02T10:00:00.000Z",
    "userId": "user-1",
}
DELETED = {**CHANGED, "entryId": "ent0000000002", "isDeleted": True, "scope": "widget"}
MAY = {"permissions": {"execute": True, "read": True, "edit": True, "admin": False}}

CASES = [
    Case(
        "datalens.audit.entries_updates_list",
        args=("2026-10-01T00:00:00Z",),
        cli=["datalens", "audit", "entries-updates-list", "--from", "2026-10-01T00:00:00Z"],
        mcp=("datalens_audit_entries_updates_list", {"from_": "2026-10-01T00:00:00Z"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getAuditEntriesUpdates", json={"from": "2026-10-01T00:00:00Z"}),
                # Measured: the last page has no `nextPageToken` at all.
                Reply(json={"entries": [CHANGED, DELETED]}),
            )
        ],
    ),
    Case(
        "datalens.audit.entries_updates_list",
        args=("2026-09-01T03:00:00+03:00",),
        kwargs={"to": "2026-09-02T00:00:00Z", "limit": 3},
        cli=[
            *("datalens", "audit", "entries-updates-list"),
            *("--from", "2026-09-01T03:00:00+03:00", "--to", "2026-09-02T00:00:00Z"),
            *("--limit", "3"),
        ],
        mcp=(
            "datalens_audit_entries_updates_list",
            {
                "from_": "2026-09-01T03:00:00+03:00",
                "to": "2026-09-02T00:00:00Z",
                "limit": 3,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getAuditEntriesUpdates",
                    json={"from": "2026-09-01T03:00:00+03:00", "to": "2026-09-02T00:00:00Z"},
                ),
                Reply(json={"entries": [CHANGED, DELETED], "nextPageToken": "t2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/getAuditEntriesUpdates",
                    json={
                        "from": "2026-09-01T03:00:00+03:00",
                        "to": "2026-09-02T00:00:00Z",
                        "pageToken": "t2",
                    },
                ),
                Reply(json={"entries": [CHANGED]}),
            ),
        ],
    ),
    Case(
        "datalens.audit.entry_permissions_get",
        args=(["ent0000000001"],),
        kwargs={"user_id": "user-1"},
        cli=["datalens", "audit", "entry-permissions-get", "ent0000000001", "--user-id", "user-1"],
        mcp=(
            "datalens_audit_entry_permissions_get",
            {"entry_ids": ["ent0000000001"], "user_id": "user-1"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getAuditEntryPermissionsForUser",
                    json={"entryIds": ["ent0000000001"], "userId": "user-1"},
                ),
                Reply(json={"ent0000000001": MAY}),
            )
        ],
    ),
    # Several entries, one of them gone: the document gives it an `error` in place of the rights.
    Case(
        "datalens.audit.entry_permissions_get",
        args=(["ent0000000003", "ent0000000004"],),
        kwargs={"user_id": "user-2"},
        cli=[
            *("datalens", "audit", "entry-permissions-get", "ent0000000003", "ent0000000004"),
            *("--user-id", "user-2"),
        ],
        mcp=(
            "datalens_audit_entry_permissions_get",
            {"entry_ids": ["ent0000000003", "ent0000000004"], "user_id": "user-2"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getAuditEntryPermissionsForUser",
                    json={"entryIds": ["ent0000000003", "ent0000000004"], "userId": "user-2"},
                ),
                Reply(json={"ent0000000003": MAY, "ent0000000004": {"error": "NOT_FOUND"}}),
            )
        ],
    ),
]
