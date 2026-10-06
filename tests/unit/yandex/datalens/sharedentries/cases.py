"""Contract cases for DataLens shared entries (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from tests.unit.yandex.datalens.collections.cases import OPERATION
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.models import AccessBindingDelta

# The keys and the roles of a live reply (2026-10-06), for a dataset that lies in a collection.
SUBJECT = {
    "subjectClaims": {"sub": "user-1", "subType": "USER_ACCOUNT", "email": "a@x"},
    "accessBindings": [{"roleId": "datalens.sharedEntries.admin", "inheritedFrom": None}],
    "inheritedAccessBindings": [
        {
            "roleId": "datalens.collections.admin",
            "inheritedFrom": {"id": "col00000000001", "type": "collection"},
        }
    ],
}
DELTA = {
    "action": "ADD",
    "accessBinding": {
        "roleId": "datalens.sharedEntries.viewer",
        "subject": {"id": "user-2", "type": "userAccount"},
    },
}

CASES = [
    Case(
        "datalens.sharedentries.access_bindings_list",
        args=("ent0000000001",),
        cli=["datalens", "sharedentries", "access-bindings-list", "ent0000000001"],
        mcp=("datalens_sharedentries_access_bindings_list", {"entry_id": "ent0000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST", "rpc/listSharedEntryAccessBindings", json={"entryId": "ent0000000001"}
                ),
                # Measured: the last page carries an empty token, not an absent one.
                Reply(json={"subjectsWithBindings": [SUBJECT], "nextPageToken": ""}),
            )
        ],
    ),
    Case(
        "datalens.sharedentries.access_bindings_list",
        args=("ent0000000002",),
        kwargs={"get_inherited_bindings": True, "limit": 30},
        cli=[
            *("datalens", "sharedentries", "access-bindings-list", "ent0000000002"),
            *("--get-inherited-bindings", "--limit", "30"),
        ],
        mcp=(
            "datalens_sharedentries_access_bindings_list",
            {"entry_id": "ent0000000002", "get_inherited_bindings": True, "limit": 30},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listSharedEntryAccessBindings",
                    json={"entryId": "ent0000000002", "getInheritedBindings": True},
                ),
                Reply(json={"subjectsWithBindings": [SUBJECT], "nextPageToken": "p2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/listSharedEntryAccessBindings",
                    json={
                        "entryId": "ent0000000002",
                        "getInheritedBindings": True,
                        "pageToken": "p2",
                    },
                ),
                Reply(json={"subjectsWithBindings": [], "nextPageToken": ""}),
            ),
        ],
    ),
    Case(
        "datalens.sharedentries.access_bindings_update",
        args=("ent0000000001",),
        kwargs={"deltas": [AccessBindingDelta.model_validate(DELTA)]},
        cli=[
            *("datalens", "sharedentries", "access-bindings-update", "ent0000000001"),
            *("--delta", json.dumps(DELTA)),
        ],
        mcp=(
            "datalens_sharedentries_access_bindings_update",
            {"entry_id": "ent0000000001", "deltas": [DELTA]},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateSharedEntryAccessBindings",
                    json={"entryId": "ent0000000001", "deltas": [DELTA]},
                ),
                Reply(json=OPERATION),
            )
        ],
    ),
]
