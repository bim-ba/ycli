"""Contract cases for DataLens collections (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.models import AccessBindingDelta

STAMPS = {
    "tenantId": "org_bpf00000000000000000",
    "createdBy": "user-1",
    "createdAt": "2026-09-01T10:00:00.000Z",
    "updatedBy": "user-1",
    "updatedAt": "2026-09-02T10:00:00.000Z",
}
SALES = {
    "collectionId": "col00000000001",
    "title": "Sales",
    "description": None,
    "parentId": None,
    "meta": {},
    **STAMPS,
}
FINANCE = {
    **SALES,
    "collectionId": "col00000000002",
    "title": "Finance",
    "parentId": SALES["collectionId"],
}
REPORTS = {**FINANCE, "collectionId": "col00000000003", "title": "Reports", "entity": "collection"}
Q1 = {
    "workbookId": "wb000000000001",
    "collectionId": SALES["collectionId"],
    "title": "Q1",
    "description": None,
    "meta": {},
    "entity": "workbook",
    **STAMPS,
}
SUBJECT = {
    "subjectClaims": {"sub": "user-1", "subType": "SUBJECT_TYPE_USER_ACCOUNT", "email": "a@x"},
    "accessBindings": [{"roleId": "datalens.collections.editor", "inheritedFrom": None}],
    "inheritedAccessBindings": [],
}

OPERATION = {
    "id": "op0000000000001",
    "description": "Update access bindings",
    "createdBy": "user-1",
    "createdAt": {"seconds": "1790000000", "nanos": 0},
    "modifiedAt": {"seconds": "1790000000", "nanos": 0},
    "metadata": {},
    "done": True,
}
DELTA = {
    "action": "ADD",
    "accessBinding": {
        "roleId": "datalens.collections.viewer",
        "subject": {"id": "user-2", "type": "userAccount"},
    },
}
MOVED = {**FINANCE, "parentId": "col00000000001"}

CASES = [
    Case(
        "datalens.collections.get",
        args=("col00000000001",),
        cli=["datalens", "collections", "get", "col00000000001"],
        mcp=("datalens_collections_get", {"collection_id": "col00000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getCollection", json={"collectionId": "col00000000001"}),
                Reply(json=SALES),
            )
        ],
    ),
    Case(
        "datalens.collections.get",
        args=("col00000000001",),
        kwargs={"include_permissions_info": True},
        cli=["datalens", "collections", "get", "col00000000001", "--include-permissions-info"],
        mcp=(
            "datalens_collections_get",
            {"collection_id": "col00000000001", "include_permissions_info": True},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getCollection",
                    json={"collectionId": "col00000000001", "includePermissionsInfo": True},
                ),
                Reply(json=SALES),
            )
        ],
    ),
    Case(
        "datalens.collections.list_by_ids",
        args=(["col00000000001", "col00000000002"],),
        cli=["datalens", "collections", "list-by-ids", "col00000000001", "col00000000002"],
        mcp=(
            "datalens_collections_list_by_ids",
            {"collection_ids": ["col00000000001", "col00000000002"]},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getCollectionsByIds",
                    json={"collectionIds": ["col00000000001", "col00000000002"]},
                ),
                Reply(json=[SALES, FINANCE]),
            )
        ],
    ),
    Case(
        "datalens.collections.content_list",
        args=("col00000000001",),
        kwargs={"limit": 45},
        cli=["datalens", "collections", "content-list", "col00000000001", "--limit", "45"],
        mcp=("datalens_collections_content_list", {"collection_id": "col00000000001", "limit": 45}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getCollectionContent", json={"collectionId": "col00000000001"}),
                Reply(json={"items": [REPORTS], "nextPageToken": "2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/getCollectionContent",
                    json={"collectionId": "col00000000001", "page": "2"},
                ),
                Reply(json={"items": [Q1], "nextPageToken": None}),
            ),
        ],
    ),
    # The root has no id: the API takes ``null`` for it, and every filter goes in the body.
    Case(
        "datalens.collections.content_list",
        args=(None,),
        kwargs={
            "limit": 45,
            "filter_string": "Q",
            "order_field": "title",
            "order_direction": "asc",
            "only_my": True,
            "mode": "onlyWorkbooks",
            "include_permissions_info": True,
        },
        cli=[
            *("datalens", "collections", "content-list", "--limit", "45"),
            *("--filter-string", "Q", "--order-field", "title", "--order-direction", "asc"),
            *("--only-my", "--mode", "onlyWorkbooks", "--include-permissions-info"),
        ],
        mcp=(
            "datalens_collections_content_list",
            {
                "limit": 45,
                "filter_string": "Q",
                "order_field": "title",
                "order_direction": "asc",
                "only_my": True,
                "mode": "onlyWorkbooks",
                "include_permissions_info": True,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getCollectionContent",
                    json={
                        "collectionId": None,
                        "filterString": "Q",
                        "orderField": "title",
                        "orderDirection": "asc",
                        "onlyMy": True,
                        "mode": "onlyWorkbooks",
                        "includePermissionsInfo": True,
                    },
                ),
                Reply(json={"items": [Q1]}),
            )
        ],
    ),
    Case(
        "datalens.collections.breadcrumbs_list",
        args=("col00000000002",),
        cli=["datalens", "collections", "breadcrumbs-list", "col00000000002"],
        mcp=("datalens_collections_breadcrumbs_list", {"collection_id": "col00000000002"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST", "rpc/getCollectionBreadcrumbs", json={"collectionId": "col00000000002"}
                ),
                Reply(json=[SALES, FINANCE]),
            )
        ],
    ),
    Case(
        "datalens.collections.permissions_get_root",
        cli=["datalens", "collections", "permissions-get-root"],
        mcp=("datalens_collections_permissions_get_root", {}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getRootCollectionPermissions"),
                Reply(json={"createCollectionInRoot": False, "createWorkbookInRoot": True}),
            )
        ],
    ),
    Case(
        "datalens.collections.access_bindings_list",
        args=("col00000000001",),
        cli=["datalens", "collections", "access-bindings-list", "col00000000001"],
        mcp=("datalens_collections_access_bindings_list", {"collection_id": "col00000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listCollectionAccessBindings",
                    json={"collectionId": "col00000000001"},
                ),
                Reply(json={"subjectsWithBindings": [SUBJECT], "nextPageToken": "t2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/listCollectionAccessBindings",
                    json={"collectionId": "col00000000001", "pageToken": "t2"},
                ),
                Reply(json={"subjectsWithBindings": [], "nextPageToken": ""}),
            ),
        ],
    ),
    Case(
        "datalens.collections.create",
        kwargs={"title": "Sales"},
        cli=["datalens", "collections", "create", "--title", "Sales"],
        mcp=("datalens_collections_create", {"title": "Sales"}),
        exchanges=[
            (
                Sent("POST", "rpc/createCollection", json={"title": "Sales", "parentId": None}),
                Reply(json={**SALES, "operation": OPERATION}),
            )
        ],
    ),
    Case(
        "datalens.collections.create",
        kwargs={"title": "Finance", "parent_id": "col00000000001", "description": "Books"},
        cli=[
            *("datalens", "collections", "create", "--title", "Finance"),
            *("--parent-id", "col00000000001", "--description", "Books"),
        ],
        mcp=(
            "datalens_collections_create",
            {"title": "Finance", "parent_id": "col00000000001", "description": "Books"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createCollection",
                    json={
                        "title": "Finance",
                        "parentId": "col00000000001",
                        "description": "Books",
                    },
                ),
                Reply(json={**FINANCE, "operation": OPERATION}),
            )
        ],
    ),
    Case(
        "datalens.collections.update",
        args=("col00000000001",),
        kwargs={"title": "Sales 2026"},
        cli=["datalens", "collections", "update", "col00000000001", "--title", "Sales 2026"],
        mcp=(
            "datalens_collections_update",
            {"collection_id": "col00000000001", "title": "Sales 2026"},
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateCollection",
                    json={"collectionId": "col00000000001", "title": "Sales 2026"},
                ),
                Reply(json={**SALES, "title": "Sales 2026"}),
            )
        ],
    ),
    Case(
        "datalens.collections.move",
        args=("col00000000002",),
        kwargs={"parent_id": "col00000000001"},
        cli=[
            *("datalens", "collections", "move", "col00000000002"),
            *("--parent-id", "col00000000001"),
        ],
        mcp=(
            "datalens_collections_move",
            {"collection_id": "col00000000002", "parent_id": "col00000000001"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/moveCollection",
                    json={"collectionId": "col00000000002", "parentId": "col00000000001"},
                ),
                Reply(json=MOVED),
            )
        ],
    ),
    # No parent is the root; the API takes ``null`` for it. With a new title on the way.
    Case(
        "datalens.collections.move",
        args=("col00000000002",),
        kwargs={"title": "Books"},
        cli=["datalens", "collections", "move", "col00000000002", "--title", "Books"],
        mcp=(
            "datalens_collections_move",
            {"collection_id": "col00000000002", "title": "Books"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/moveCollection",
                    json={"collectionId": "col00000000002", "parentId": None, "title": "Books"},
                ),
                Reply(json={**FINANCE, "parentId": None, "title": "Books"}),
            )
        ],
    ),
    Case(
        "datalens.collections.move_bulk",
        args=(["col00000000002", "col00000000003"],),
        kwargs={"parent_id": "col00000000001"},
        cli=[
            *("datalens", "collections", "move-bulk", "col00000000002", "col00000000003"),
            *("--parent-id", "col00000000001"),
        ],
        mcp=(
            "datalens_collections_move_bulk",
            {
                "collection_ids": ["col00000000002", "col00000000003"],
                "parent_id": "col00000000001",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/moveCollections",
                    json={
                        "collectionIds": ["col00000000002", "col00000000003"],
                        "parentId": "col00000000001",
                    },
                ),
                Reply(json={"collections": [MOVED, {**MOVED, "collectionId": "col00000000003"}]}),
            )
        ],
    ),
    Case(
        "datalens.collections.delete",
        args=("col00000000001",),
        cli=["datalens", "collections", "delete", "col00000000001"],
        mcp=("datalens_collections_delete", {"collection_id": "col00000000001"}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent("POST", "rpc/deleteCollection", json={"collectionId": "col00000000001"}),
                Reply(json={"collections": [SALES, FINANCE]}),
            )
        ],
    ),
    Case(
        "datalens.collections.delete_bulk",
        args=(["col00000000001", "col00000000002"],),
        cli=["datalens", "collections", "delete-bulk", "col00000000001", "col00000000002"],
        mcp=(
            "datalens_collections_delete_bulk",
            {"collection_ids": ["col00000000001", "col00000000002"]},
        ),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/deleteCollections",
                    json={"collectionIds": ["col00000000001", "col00000000002"]},
                ),
                Reply(json={"collections": [SALES, FINANCE]}),
            )
        ],
    ),
    Case(
        "datalens.collections.access_bindings_update",
        args=("col00000000001",),
        kwargs={"deltas": [AccessBindingDelta.model_validate(DELTA)]},
        cli=[
            *("datalens", "collections", "access-bindings-update", "col00000000001"),
            *("--delta", json.dumps(DELTA)),
        ],
        mcp=(
            "datalens_collections_access_bindings_update",
            {"collection_id": "col00000000001", "deltas": [DELTA]},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateCollectionAccessBindings",
                    json={"collectionId": "col00000000001", "deltas": [DELTA]},
                ),
                Reply(json=OPERATION),
            )
        ],
    ),
]
