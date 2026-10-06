"""Contract cases for DataLens permissions (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

# The shape of a live reply (2026-10-06): a map by id; a missing object answers an error.
FOUND = {"permissions": {"view": True, "update": True, "delete": False}}
MISSING = {"error": "NOT_FOUND"}

CASES = [
    Case(
        "datalens.permissions.get_bulk",
        kwargs={"workbook_ids": ["wb000000000001", "wb000000000009"]},
        cli=[
            *("datalens", "permissions", "get-bulk"),
            *("--workbook-id", "wb000000000001", "--workbook-id", "wb000000000009"),
        ],
        mcp=(
            "datalens_permissions_get_bulk",
            {"workbook_ids": ["wb000000000001", "wb000000000009"]},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getPermissionsBulk",
                    json={"workbookIds": ["wb000000000001", "wb000000000009"]},
                ),
                Reply(
                    json={
                        "entries": {},
                        "workbooks": {"wb000000000001": FOUND, "wb000000000009": MISSING},
                        "collections": {},
                    }
                ),
            )
        ],
    ),
    Case(
        "datalens.permissions.get_bulk",
        kwargs={
            "entry_ids": ["ent00000000001"],
            "workbook_ids": ["wb000000000001"],
            "collection_ids": ["col00000000001"],
        },
        cli=[
            *("datalens", "permissions", "get-bulk", "--entry-id", "ent00000000001"),
            *("--workbook-id", "wb000000000001", "--collection-id", "col00000000001"),
        ],
        mcp=(
            "datalens_permissions_get_bulk",
            {
                "entry_ids": ["ent00000000001"],
                "workbook_ids": ["wb000000000001"],
                "collection_ids": ["col00000000001"],
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getPermissionsBulk",
                    json={
                        "entryIds": ["ent00000000001"],
                        "workbookIds": ["wb000000000001"],
                        "collectionIds": ["col00000000001"],
                    },
                ),
                Reply(
                    json={
                        "entries": {"ent00000000001": {"permissions": {"read": True}}},
                        "workbooks": {"wb000000000001": FOUND},
                        "collections": {"col00000000001": {"permissions": {"view": True}}},
                    }
                ),
            )
        ],
    ),
]
