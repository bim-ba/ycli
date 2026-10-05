"""Contract cases for DataLens workbooks (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from tests.unit.yandex.datalens.collections.cases import DELTA, OPERATION, STAMPS
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.models import AccessBindingDelta
from ycli.yandex.datalens.workbooks.models import EntriesFilters, EntriesOrder

Q1 = {
    "workbookId": "wb000000000001",
    "collectionId": "col00000000001",
    "title": "Q1",
    "description": None,
    "meta": {},
    **STAMPS,
}
Q2 = {**Q1, "workbookId": "wb000000000002", "title": "Q2"}
# The specification makes ``permissions`` a required field of one workbook's reply.
PERMISSIONS = dict.fromkeys(
    (
        *("listAccessBindings", "updateAccessBindings", "limitedView", "view", "update"),
        *("copy", "move", "publish", "embed", "delete"),
    ),
    True,
)
Q1_DETAILS = {**Q1, "permissions": PERMISSIONS}
SUBJECT = {
    "subjectClaims": {"sub": "user-1", "subType": "SUBJECT_TYPE_USER_ACCOUNT", "email": "a@x"},
    "accessBindings": [{"roleId": "datalens.workbooks.editor", "inheritedFrom": None}],
    "inheritedAccessBindings": [],
}
ORDERS = {"entryId": "ent00000000001", "scope": "dataset", "key": "Sales/orders", **STAMPS}
OVERVIEW = {"entryId": "ent00000000002", "scope": "dash", "key": "Sales/overview", **STAMPS}
ORDER = {"field": "name", "direction": "asc"}
FILTERS = {"name": "sales"}

CASES = [
    Case(
        "datalens.workbooks.get",
        args=("wb000000000001",),
        cli=["datalens", "workbooks", "get", "wb000000000001"],
        mcp=("datalens_workbooks_get", {"workbook_id": "wb000000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getWorkbook", json={"workbookId": "wb000000000001"}),
                Reply(json=Q1_DETAILS),
            )
        ],
    ),
    Case(
        "datalens.workbooks.get",
        args=("wb000000000001",),
        kwargs={"include_permissions_info": True},
        cli=["datalens", "workbooks", "get", "wb000000000001", "--include-permissions-info"],
        mcp=(
            "datalens_workbooks_get",
            {"workbook_id": "wb000000000001", "include_permissions_info": True},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getWorkbook",
                    json={"workbookId": "wb000000000001", "includePermissionsInfo": True},
                ),
                Reply(json=Q1_DETAILS),
            )
        ],
    ),
    Case(
        "datalens.workbooks.list",
        kwargs={"collection_id": "col00000000001", "limit": 45},
        cli=[
            *("datalens", "workbooks", "list"),
            *("--collection-id", "col00000000001", "--limit", "45"),
        ],
        mcp=("datalens_workbooks_list", {"collection_id": "col00000000001", "limit": 45}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getWorkbooksList", json={"collectionId": "col00000000001"}),
                Reply(json={"workbooks": [Q1], "nextPageToken": "1"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/getWorkbooksList",
                    json={"collectionId": "col00000000001", "page": 1},
                ),
                Reply(json={"workbooks": [Q2]}),
            ),
        ],
    ),
    # The root: no collection is named, and every filter goes in the body.
    Case(
        "datalens.workbooks.list",
        kwargs={
            "limit": 45,
            "filter_string": "Q",
            "order_field": "title",
            "order_direction": "asc",
            "only_my": True,
            "include_permissions_info": True,
        },
        cli=[
            *("datalens", "workbooks", "list", "--limit", "45", "--filter-string", "Q"),
            *("--order-field", "title", "--order-direction", "asc"),
            *("--only-my", "--include-permissions-info"),
        ],
        mcp=(
            "datalens_workbooks_list",
            {
                "limit": 45,
                "filter_string": "Q",
                "order_field": "title",
                "order_direction": "asc",
                "only_my": True,
                "include_permissions_info": True,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getWorkbooksList",
                    json={
                        "filterString": "Q",
                        "orderField": "title",
                        "orderDirection": "asc",
                        "onlyMy": True,
                        "includePermissionsInfo": True,
                    },
                ),
                Reply(json={"workbooks": [Q1, Q2]}),
            )
        ],
    ),
    Case(
        "datalens.workbooks.list_by_ids",
        args=(["wb000000000001", "wb000000000002"],),
        cli=["datalens", "workbooks", "list-by-ids", "wb000000000001", "wb000000000002"],
        mcp=(
            "datalens_workbooks_list_by_ids",
            {"workbook_ids": ["wb000000000001", "wb000000000002"]},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getWorkbooksByIds",
                    json={"workbookIds": ["wb000000000001", "wb000000000002"]},
                ),
                Reply(json=[Q1, Q2]),
            )
        ],
    ),
    Case(
        "datalens.workbooks.access_bindings_list",
        args=("wb000000000001",),
        kwargs={"get_inherited_bindings": True},
        cli=[
            *("datalens", "workbooks", "access-bindings-list", "wb000000000001"),
            "--get-inherited-bindings",
        ],
        mcp=(
            "datalens_workbooks_access_bindings_list",
            {"workbook_id": "wb000000000001", "get_inherited_bindings": True},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listWorkbookAccessBindings",
                    json={"workbookId": "wb000000000001", "getInheritedBindings": True},
                ),
                Reply(json={"subjectsWithBindings": [SUBJECT], "nextPageToken": ""}),
            )
        ],
    ),
    Case(
        "datalens.workbooks.entries_list",
        args=("wb000000000001",),
        kwargs={"limit": 45},
        cli=["datalens", "workbooks", "entries-list", "wb000000000001", "--limit", "45"],
        mcp=("datalens_workbooks_entries_list", {"workbook_id": "wb000000000001", "limit": 45}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getWorkbookEntries", json={"workbookId": "wb000000000001"}),
                Reply(json={"entries": [ORDERS], "nextPageToken": "1"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/getWorkbookEntries",
                    json={"workbookId": "wb000000000001", "page": 1},
                ),
                Reply(json={"entries": [OVERVIEW]}),
            ),
        ],
    ),
    # Every filter: several kinds go as a list, the order and the filter as objects.
    Case(
        "datalens.workbooks.entries_list",
        args=("wb000000000001",),
        kwargs={
            "limit": 45,
            "include_permissions_info": True,
            "only_my": True,
            "created_by": "user-1",
            "scope": ["dataset", "dash"],
            "order_by": EntriesOrder.model_validate(ORDER),
            "filters": EntriesFilters.model_validate(FILTERS),
        },
        cli=[
            *("datalens", "workbooks", "entries-list", "wb000000000001", "--limit", "45"),
            *("--include-permissions-info", "--only-my", "--created-by", "user-1"),
            *("--scope", "dataset", "--scope", "dash"),
            *("--order-by", json.dumps(ORDER), "--filters", json.dumps(FILTERS)),
        ],
        mcp=(
            "datalens_workbooks_entries_list",
            {
                "workbook_id": "wb000000000001",
                "limit": 45,
                "include_permissions_info": True,
                "only_my": True,
                "created_by": "user-1",
                "scope": ["dataset", "dash"],
                "order_by": ORDER,
                "filters": FILTERS,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getWorkbookEntries",
                    json={
                        "workbookId": "wb000000000001",
                        "includePermissionsInfo": True,
                        "onlyMy": True,
                        "createdBy": "user-1",
                        "scope": ["dataset", "dash"],
                        "orderBy": ORDER,
                        "filters": FILTERS,
                    },
                ),
                Reply(json={"entries": [ORDERS, OVERVIEW]}),
            )
        ],
    ),
    Case(
        "datalens.workbooks.create",
        kwargs={"title": "Q1", "collection_id": "col00000000001", "description": "First"},
        cli=[
            *("datalens", "workbooks", "create", "--title", "Q1"),
            *("--collection-id", "col00000000001", "--description", "First"),
        ],
        mcp=(
            "datalens_workbooks_create",
            {"title": "Q1", "collection_id": "col00000000001", "description": "First"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createWorkbook",
                    json={"title": "Q1", "collectionId": "col00000000001", "description": "First"},
                ),
                Reply(json={**Q1, "operation": OPERATION}),
            )
        ],
    ),
    # No collection is the root: the field is optional here, so it is left out.
    Case(
        "datalens.workbooks.create",
        kwargs={"title": "Q1"},
        cli=["datalens", "workbooks", "create", "--title", "Q1"],
        mcp=("datalens_workbooks_create", {"title": "Q1"}),
        exchanges=[
            (
                Sent("POST", "rpc/createWorkbook", json={"title": "Q1"}),
                Reply(json={**Q1, "collectionId": None, "operation": OPERATION}),
            )
        ],
    ),
    Case(
        "datalens.workbooks.update",
        args=("wb000000000001",),
        kwargs={"title": "Q1 2026"},
        cli=["datalens", "workbooks", "update", "wb000000000001", "--title", "Q1 2026"],
        mcp=("datalens_workbooks_update", {"workbook_id": "wb000000000001", "title": "Q1 2026"}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateWorkbook",
                    json={"workbookId": "wb000000000001", "title": "Q1 2026"},
                ),
                Reply(json={**Q1, "title": "Q1 2026"}),
            )
        ],
    ),
    Case(
        "datalens.workbooks.move",
        args=("wb000000000001",),
        kwargs={"collection_id": "col00000000002"},
        cli=[
            *("datalens", "workbooks", "move", "wb000000000001"),
            *("--collection-id", "col00000000002"),
        ],
        mcp=(
            "datalens_workbooks_move",
            {"workbook_id": "wb000000000001", "collection_id": "col00000000002"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/moveWorkbook",
                    json={"workbookId": "wb000000000001", "collectionId": "col00000000002"},
                ),
                Reply(json={**Q1, "collectionId": "col00000000002"}),
            )
        ],
    ),
    # No collection is the root; the API requires the field and takes ``null`` for it.
    Case(
        "datalens.workbooks.move",
        args=("wb000000000001",),
        kwargs={"title": "First"},
        cli=["datalens", "workbooks", "move", "wb000000000001", "--title", "First"],
        mcp=("datalens_workbooks_move", {"workbook_id": "wb000000000001", "title": "First"}),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/moveWorkbook",
                    json={"workbookId": "wb000000000001", "collectionId": None, "title": "First"},
                ),
                Reply(json={**Q1, "collectionId": None, "title": "First"}),
            )
        ],
    ),
    Case(
        "datalens.workbooks.move_bulk",
        args=(["wb000000000001", "wb000000000002"],),
        kwargs={"collection_id": "col00000000002"},
        cli=[
            *("datalens", "workbooks", "move-bulk", "wb000000000001", "wb000000000002"),
            *("--collection-id", "col00000000002"),
        ],
        mcp=(
            "datalens_workbooks_move_bulk",
            {
                "workbook_ids": ["wb000000000001", "wb000000000002"],
                "collection_id": "col00000000002",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/moveWorkbooks",
                    json={
                        "workbookIds": ["wb000000000001", "wb000000000002"],
                        "collectionId": "col00000000002",
                    },
                ),
                Reply(json={"workbooks": [Q1, Q2]}),
            )
        ],
    ),
    Case(
        "datalens.workbooks.delete",
        args=("wb000000000001",),
        cli=["datalens", "workbooks", "delete", "wb000000000001"],
        mcp=("datalens_workbooks_delete", {"workbook_id": "wb000000000001"}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent("POST", "rpc/deleteWorkbook", json={"workbookId": "wb000000000001"}),
                Reply(json=Q1),
            )
        ],
    ),
    Case(
        "datalens.workbooks.delete_bulk",
        args=(["wb000000000001", "wb000000000002"],),
        cli=["datalens", "workbooks", "delete-bulk", "wb000000000001", "wb000000000002"],
        mcp=(
            "datalens_workbooks_delete_bulk",
            {"workbook_ids": ["wb000000000001", "wb000000000002"]},
        ),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/deleteWorkbooks",
                    json={"workbookIds": ["wb000000000001", "wb000000000002"]},
                ),
                Reply(json={"workbooks": [Q1, Q2]}),
            )
        ],
    ),
    Case(
        "datalens.workbooks.access_bindings_update",
        args=("wb000000000001",),
        kwargs={"deltas": [AccessBindingDelta.model_validate(DELTA)]},
        cli=[
            *("datalens", "workbooks", "access-bindings-update", "wb000000000001"),
            *("--delta", json.dumps(DELTA)),
        ],
        mcp=(
            "datalens_workbooks_access_bindings_update",
            {"workbook_id": "wb000000000001", "deltas": [DELTA]},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateWorkbookAccessBindings",
                    json={"workbookId": "wb000000000001", "deltas": [DELTA]},
                ),
                Reply(json=OPERATION),
            )
        ],
    ),
]
