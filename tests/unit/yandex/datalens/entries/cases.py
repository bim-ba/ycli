"""Contract cases for DataLens entries (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.entries.models import ListFilters, ListOrder

ORDERS = {"entryId": "ent00000000001", "scope": "dataset", "key": "Sales/orders"}
OVERVIEW = {"entryId": "ent00000000002", "scope": "dash", "key": "Sales/overview"}
MARGIN = {"entryId": "ent00000000003", "scope": "dash", "key": "Sales/margin"}
# An entry the caller may not read: the flag and little else.
LOCKED = {"entryId": "ent00000000004", "scope": "dash", "isLocked": True}
ORDER = {"field": "name", "direction": "asc"}
FILTERS = {"name": "sales"}

CASES = [
    Case(
        "datalens.entries.list",
        kwargs={"scope": "dash", "limit": 45},
        cli=["datalens", "entries", "list", "--scope", "dash", "--limit", "45"],
        mcp=("datalens_entries_list", {"scope": "dash", "limit": 45}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getEntries", json={"scope": "dash"}),
                Reply(json={"entries": [OVERVIEW], "nextPageToken": "t2"}),
            ),
            (
                Sent("POST", "rpc/getEntries", json={"scope": "dash", "pageToken": "t2"}),
                Reply(json={"entries": [MARGIN]}),
            ),
        ],
    ),
    # Every filter. The API's own shape of an entry the caller may not read is LOCKED.
    Case(
        "datalens.entries.list",
        kwargs={
            "limit": 45,
            "ids": ["ent00000000002"],
            "scopes": ["dash", "widget"],
            "type": ["table"],
            "created_by": ["user-1"],
            "order_by": ListOrder.model_validate(ORDER),
            "exclude_locked": True,
            "include_links": True,
            "filters": ListFilters.model_validate(FILTERS),
            "include_permissions_info": True,
            "ignore_workbook_entries": True,
            "ignore_shared_entries": True,
            "include_data": True,
        },
        cli=[
            *("datalens", "entries", "list", "--limit", "45", "--id", "ent00000000002"),
            *("--scopes", "dash", "--scopes", "widget", "--type", "table"),
            *("--created-by", "user-1", "--order-by", json.dumps(ORDER)),
            *("--exclude-locked", "--include-links", "--filters", json.dumps(FILTERS)),
            *("--include-permissions-info", "--ignore-workbook-entries"),
            *("--ignore-shared-entries", "--include-data"),
        ],
        mcp=(
            "datalens_entries_list",
            {
                "limit": 45,
                "ids": ["ent00000000002"],
                "scopes": ["dash", "widget"],
                "type": ["table"],
                "created_by": ["user-1"],
                "order_by": ORDER,
                "exclude_locked": True,
                "include_links": True,
                "filters": FILTERS,
                "include_permissions_info": True,
                "ignore_workbook_entries": True,
                "ignore_shared_entries": True,
                "include_data": True,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getEntries",
                    json={
                        "ids": ["ent00000000002"],
                        "scopes": ["dash", "widget"],
                        "type": ["table"],
                        "createdBy": ["user-1"],
                        "orderBy": ORDER,
                        "excludeLocked": True,
                        "includeLinks": True,
                        "filters": FILTERS,
                        "includePermissionsInfo": True,
                        "ignoreWorkbookEntries": True,
                        "ignoreSharedEntries": True,
                        "includeData": True,
                    },
                ),
                Reply(json={"entries": [OVERVIEW], "nextPageToken": ""}),
            )
        ],
    ),
    Case(
        "datalens.entries.list",
        kwargs={"scopes": ["dash"]},
        cli=["datalens", "entries", "list", "--scopes", "dash"],
        mcp=("datalens_entries_list", {"scopes": ["dash"]}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getEntries", json={"scopes": ["dash"]}),
                Reply(json={"entries": [OVERVIEW, LOCKED]}),
            )
        ],
    ),
    Case(
        "datalens.entries.relations_list",
        args=(["ent00000000002"],),
        kwargs={"link_direction": "from"},
        cli=[
            *("datalens", "entries", "relations-list", "ent00000000002"),
            *("--link-direction", "from"),
        ],
        mcp=(
            "datalens_entries_relations_list",
            {"entry_ids": ["ent00000000002"], "link_direction": "from"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getEntriesRelations",
                    json={"entryIds": ["ent00000000002"], "linkDirection": "from"},
                ),
                Reply(json={"relations": [ORDERS]}),
            )
        ],
    ),
    Case(
        "datalens.entries.relations_list",
        args=(["ent00000000001"],),
        kwargs={"limit": 45, "include_permissions_info": True, "scope": "dash"},
        cli=[
            *("datalens", "entries", "relations-list", "ent00000000001", "--limit", "45"),
            *("--include-permissions-info", "--scope", "dash"),
        ],
        mcp=(
            "datalens_entries_relations_list",
            {
                "entry_ids": ["ent00000000001"],
                "limit": 45,
                "include_permissions_info": True,
                "scope": "dash",
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getEntriesRelations",
                    json={
                        "entryIds": ["ent00000000001"],
                        "includePermissionsInfo": True,
                        "scope": "dash",
                    },
                ),
                Reply(json={"relations": [OVERVIEW], "nextPageToken": "t2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/getEntriesRelations",
                    json={
                        "entryIds": ["ent00000000001"],
                        "includePermissionsInfo": True,
                        "scope": "dash",
                        "pageToken": "t2",
                    },
                ),
                Reply(json={"relations": [MARGIN], "nextPageToken": ""}),
            ),
        ],
    ),
    Case(
        "datalens.entries.permissions_get",
        args=(["ent00000000001", "ent00000000009"],),
        cli=["datalens", "entries", "permissions-get", "ent00000000001", "ent00000000009"],
        mcp=(
            "datalens_entries_permissions_get",
            {"entry_ids": ["ent00000000001", "ent00000000009"]},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getEntriesPermissions",
                    json={"entryIds": ["ent00000000001", "ent00000000009"]},
                ),
                # The shape of a live reply (2026-10-06).
                Reply(
                    json={
                        "ent00000000001": {
                            "permissions": {
                                "execute": True,
                                "read": True,
                                "edit": False,
                                "admin": False,
                            }
                        },
                        "ent00000000009": {"error": "NOT_FOUND"},
                    }
                ),
            )
        ],
    ),
    Case(
        "datalens.entries.revisions_list",
        args=("ent00000000001",),
        kwargs={"limit": 45},
        cli=["datalens", "entries", "revisions-list", "ent00000000001", "--limit", "45"],
        mcp=("datalens_entries_revisions_list", {"entry_id": "ent00000000001", "limit": 45}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getRevisions", json={"entryId": "ent00000000001"}),
                Reply(json={"entries": [{"revId": "rev2"}], "nextPageToken": "t2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/getRevisions",
                    json={"entryId": "ent00000000001", "pageToken": "t2"},
                ),
                Reply(json={"entries": [{"revId": "rev1"}]}),
            ),
        ],
    ),
    Case(
        "datalens.entries.revisions_list",
        args=("ent00000000001",),
        kwargs={"rev_ids": ["rev1"]},
        cli=["datalens", "entries", "revisions-list", "ent00000000001", "--rev-id", "rev1"],
        mcp=(
            "datalens_entries_revisions_list",
            {"entry_id": "ent00000000001", "rev_ids": ["rev1"]},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getRevisions",
                    json={"entryId": "ent00000000001", "revIds": ["rev1"]},
                ),
                Reply(json={"entries": [{"revId": "rev1"}]}),
            )
        ],
    ),
    Case(
        "datalens.entries.rename",
        args=("ent00000000001",),
        kwargs={"name": "orders 2026"},
        cli=["datalens", "entries", "rename", "ent00000000001", "--name", "orders 2026"],
        mcp=("datalens_entries_rename", {"entry_id": "ent00000000001", "name": "orders 2026"}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/renameEntry",
                    json={"entryId": "ent00000000001", "name": "orders 2026"},
                ),
                Reply(json=[{**ORDERS, "key": "Sales/orders 2026"}]),
            )
        ],
    ),
]
